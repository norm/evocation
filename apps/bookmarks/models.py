# encoding: utf-8

import os
import subprocess

from biplist import readPlist as read_plist
from bs4 import BeautifulSoup
from redis import Redis
import requests
from tempfile import mkstemp, NamedTemporaryFile
from urlparse import urlparse, urljoin

from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.core.files import File
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.html import escape

from haystack import connections
from pinboard import Pinboard
from taggit.managers import TaggableManager
from taggit.utils import parse_tags, edit_string_for_tags

from .tasks import update_bookmark_archive, update_site_favicon, push_to_pinboard


ORIGINS = (
    (1, 'User'),
    (2, 'Pinboard'),
)

class PubSubMixin(object):
    def save(self, *args, **kwargs):
        super(PubSubMixin, self).save(*args, **kwargs)
        self.publish_save_message()

    def publish_save_message(self):
        self.publish_message(self.save_message_text())

    def publish_message(self, text, channel='chatter.evocation'):
        redis = Redis()
        redis.publish(channel, text)

    def save_message_text(self):
        return u'Saved %s' % (self.__unicode__())


class Bookmark(PubSubMixin, models.Model):
    url = models.URLField(max_length=2000, unique=True)
    title = models.CharField(max_length=1024, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    site = models.ForeignKey('Website', related_name='bookmarks', null=True, blank=True)
    origin = models.IntegerField(choices=ORIGINS, default=1)
    tags = TaggableManager()

    def save(self, *args, **kwargs):
        if not self.site:
            site, created = Website.objects.get_or_create(domain = self.get_url_domain())
            self.site = site
        super(Bookmark, self).save(*args, **kwargs)
        self.create_first_archive()

        if self.origin == 1 and settings.PINBOARD_PUSH:
            # title is required (and if not set on first creation
            # will be after an archive is fetched)
            if self.title:
                push_to_pinboard(self.pk)

    def add_tag(self, tag):
        self.tags.add(tag)
        self.save()

    def add_tags(self, tags_string):
        for tag in parse_tags(tags_string):
            self.add_tag(tag)

    def remove_tag(self, tag):
        self.tags.remove(tag)
        self.save()

    def tags_as_string(self):
        return edit_string_for_tags(self.tags.all())

    def get_absolute_url(self):
        return reverse('bookmark-detail', kwargs={'pk': self.pk})

    def update_archive(self):
        update_bookmark_archive.delay(self.pk)

    def create_first_archive(self):
        if self.archives.count() == 0:
            self.update_archive()

    def latest_archive(self):
        if self.archives.count() > 0:
            return self.archives.all()[0]
        else:
            return None

    def archived_title(self):
        body = self.get_archive_body()
        if body is not None:
            soup = BeautifulSoup(body, 'html5lib')
            return soup.title.text
        return None

    def archived_text(self):
        body = self.get_archive_body()
        if body is not None:
            soup = BeautifulSoup(body, 'html5lib')
            for element in soup(['script', 'style', 'svg']):
                element.replace_with('')
            return soup.body.get_text()
        return None

    def archived_text_for_search_indexing(self):
        body = self.archived_text()
        words = []
        for word in body.split():
            # terms in xapian limited to 245 chars after they're HTML escaped
            if len(escape(word)) < 245:
                words.append(word)
        return ' '.join(words)

    def get_archive_body(self):
        latest = self.latest_archive()
        if latest is not None and latest.archive:
            plist = read_plist(latest.archive.file)
            return plist['WebMainResource']['WebResourceData']
        return None

    def update_search_index(self):
        connections['default'].get_unified_index().get_index(Bookmark).update_object(self)
        self.register_favicon()

    def register_favicon(self):
        body = self.get_archive_body()
        if body is not None:
            soup = BeautifulSoup(body, 'html5lib')
            link = soup.find('link', rel='shortcut icon')
            icon = None
            if link:
                icon = link['href']
            else:
                link = soup.find('link', rel='Shortcut Icon')
                if link:
                    icon = link['href']
                else:
                    link = soup.find('link', rel='icon')
                    if link:
                        icon = link['href']
            
            if not icon:
                icon = '/favicon.ico'

            icon = urljoin(self.url, icon)
            update_site_favicon.delay(self.get_url_domain(), icon)

    def save_message_text(self):
        return u'Saved %s — http://bookmarks.dev%s' % (self.__unicode__(), self.get_absolute_url())

    def get_url_domain(self):
        domain = urlparse(self.url)[1]
        if domain.startswith('www.'):
            return domain[4:]
        else:
            return domain

    def name(self):
        return self.__unicode__()

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return self.url

    class Meta:
        ordering = ["-date_added"]


class BookmarkArchive(PubSubMixin, models.Model):
    bookmark = models.ForeignKey(Bookmark, related_name='archives')
    taken = models.DateTimeField(default=timezone.now)
    archive = models.FileField(upload_to='bookmark/%Y/%m/%d', null=True, blank=True)
    screengrab = models.ImageField(upload_to='bookmark/%Y/%m/%d', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='bookmark/%Y/%m/%d', null=True, blank=True)

    def save(self, *args, **kwargs):
        super(BookmarkArchive, self).save(*args, **kwargs)
        if not self.archive:
            self.fetch_webarchive()
        if not self.screengrab:
            self.take_screengrab()

    def filename(self, extension):
        return '%s.%s' % (self.bookmark.pk, extension)

    def fetch_webarchive(self):
        handle, temp_file = mkstemp('.webarchive')
        os.close(handle)

        try:
            subprocess.check_call([
                'webarchiver',
                '-url',    self.bookmark.url,
                '-output', temp_file,
            ])
        except subprocess.CalledProcessError:
            self.publish_message('Error creating archive of %s [%d]' % (
                self.bookmark.url,
                self.bookmark.pk,
            ))
            return

        with open(temp_file, 'rb') as handle:
            model_file = File(handle)
            filename = self.filename('webarchive')
            self.archive.save(filename, model_file)

        os.remove(temp_file)

        self.publish_message('Fetched archive of %s' % self.bookmark.url)

        # check for a title if we don't already have one
        if not self.bookmark.title:
            self.bookmark.title = self.bookmark.archived_title()
            self.bookmark.save()

        self.bookmark.update_search_index()

    def take_screengrab(self):
        if not self.archive:
            self.fetch_webarchive()

        handle, temp_file = mkstemp()
        os.close(handle)

        archive_as_url = 'file://%s/%s' % (settings.MEDIA_ROOT, self.archive)
        try:
            subprocess.check_call([
                'webkit2png',
                '--width=1280',
                '--fullsize',
                '--clipped',
                '--clipwidth=320',
                '--clipheight=240',
                '-o', temp_file,
                archive_as_url
            ])
        except subprocess.CalledProcessError:
            self.publish_message('Error (subprocess) creating screenshot of %s [%d]' % (
                self.bookmark.url,
                self.bookmark.pk,
            ))
            return

        # sometimes webkit2png times out, but doesn't return an error value
        full_image = '%s-full.png' % temp_file
        thumbnail = '%s-clipped.png' % temp_file
        if os.path.isfile(full_image):
            # save full image
            with open(full_image, 'rb') as handle:
                model_file = File(handle)
                filename = self.filename('full.png')
                self.screengrab.save(filename, model_file, save=False)

            # save thumbnail
            with open(thumbnail, 'rb') as handle:
                model_file = File(handle)
                filename = self.filename('clipped.png')
                self.thumbnail.save(filename, model_file)

            os.remove(full_image)
            os.remove(thumbnail)
            os.remove(temp_file)
        else:
            self.publish_message('Error (file not found) creating screenshot of %s [%d]' % (
                self.bookmark.url,
                self.bookmark.pk,
            ))

    def publish_save_message(self):
        pass

    def __unicode__(self):
        taken = self.taken.strftime('%FT%T')
        return u'%s - %s' % (taken, self.bookmark)

    class Meta:
        ordering = ["-taken"]


class Website(models.Model):
    domain = models.CharField(max_length=2000)
    favicon = models.ImageField(upload_to='favicon/', null=True, blank=True)

    def update_favicon(self, icon):
        url = urlparse(icon)
        path, ext = os.path.splitext(icon)
        filename = '%s%s' % (self.domain, ext)
        req = requests.get(icon)

        if req.status_code == 200:
            temp_file = NamedTemporaryFile(suffix=ext)
            temp_file.write(req.content)
            temp_file.flush()
            self.favicon.save(filename, File(temp_file), save=True)
        else:
            self.publish_message('Error %d fetching favicon %s for %s' % (
                req.status_code,
                icon,
                self.domain,
            ))

    def __unicode__(self):
        return self.domain
