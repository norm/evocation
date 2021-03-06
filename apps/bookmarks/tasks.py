# encoding: utf-8

from __future__ import absolute_import
from datetime import datetime
import subprocess

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils import timezone

from celery import shared_task
from pinboard import Pinboard


@shared_task
def update_bookmark_archive(pk):
    from .models import Bookmark

    bookmark = Bookmark.objects.get(pk=pk)
    bookmark.archives.create()


@shared_task
def update_site_favicon(domain, icon):
    from .models import Website

    print '** Updating %s favicon with %s' % (domain, icon)
    site, created = Website.objects.get_or_create(domain = domain)
    site.update_favicon(icon)


@shared_task
def pull_from_pinboard():
    from .models import Bookmark

    print '** Pulling new bookmarks from Pinboard'
    pb = Pinboard(settings.PINBOARD_AUTH)
    recent = pb.posts.recent()
    val = URLValidator()

    for bookmark in recent['posts']:
        try:
            val(bookmark.url)
        except (ValidationError, ValueError) as e:
            print ' ** ', e, bookmark.url
            continue

        timestamp = timezone.make_aware(
            bookmark.time,
            timezone.get_current_timezone()
        )

        db_bookmark, created = Bookmark.objects.get_or_create(
            defaults = {
                'title': bookmark.description,
                'description': bookmark.extended,
                'date_added': timestamp,
                'origin': 2,
            },
            url = bookmark.url,
        )
        if created:
            print '-- New bookmark created [%d] %s' % (db_bookmark.pk, db_bookmark)
            for tag in bookmark.tags:
                if tag:
                    db_bookmark.tags.add(tag)


@shared_task
def push_to_pinboard(pk):
    from .models import Bookmark

    bookmark = Bookmark.objects.get(pk=pk)

    print '** Pushing bookmark to Pinboard — [%d] %s' % (bookmark.pk, bookmark)
    pb = Pinboard(settings.PINBOARD_AUTH)
    pb.posts.add(
        url = bookmark.url,
        description = unicode(bookmark.title).encode('utf-8'),
        extended = unicode(bookmark.description).encode('utf-8'),
        tags = unicode(bookmark.tags_as_string()).encode('utf-8'),
    )


@shared_task
def run_backups():
    subprocess.check_call(['sh', 'backup.sh'])
