import os
import subprocess

from tempfile import mkstemp

from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

from taggit.managers import TaggableManager
from taggit.utils import parse_tags

from .tasks import update_bookmark_archive


class Bookmark(models.Model):
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=1024, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    tags = TaggableManager()

    def save(self, *args, **kwargs):
        super(Bookmark, self).save(*args, **kwargs)
        self.create_first_archive()

    def add_tag(self, tag):
        self.tags.add(tag)
        self.save()

    def add_tags(self, tags_string):
        for tag in parse_tags(tags_string):
            self.add_tag(tag)

    def remove_tag(self, tag):
        self.tags.remove(tag)
        self.save()

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

    def name(self):
        return self.__unicode__()

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return self.url

    class Meta:
        ordering = ["-date_added"]


class BookmarkArchive(models.Model):
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

        subprocess.check_call([
            'webarchiver',
            '-url',    self.bookmark.url,
            '-output', temp_file,
        ])
        with open(temp_file, 'rb') as handle:
            model_file = File(handle)
            filename = self.filename('webarchive')
            self.archive.save(filename, model_file)

        os.remove(temp_file)

    def take_screengrab(self):
        if not self.archive:
            self.fetch_webarchive()

        handle, temp_file = mkstemp()
        os.close(handle)

        archive_as_url = 'file://%s/%s' % (settings.MEDIA_ROOT, self.archive)
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

        # save full image
        with open('%s-full.png' % temp_file, 'rb') as handle:
            model_file = File(handle)
            filename = self.filename('full.png')
            self.screengrab.save(filename, model_file, save=False)

        # save thumbnail
        with open('%s-clipped.png' % temp_file, 'rb') as handle:
            model_file = File(handle)
            filename = self.filename('clipped.png')
            self.thumbnail.save(filename, model_file)

        os.remove(temp_file)

    def __unicode__(self):
        taken = self.taken.strftime('%FT%T')
        return u'%s - %s' % (taken, self.bookmark)

    class Meta:
        ordering = ["-taken"]
