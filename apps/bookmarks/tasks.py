from __future__ import absolute_import
from datetime import datetime

from django.conf import settings
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

    site, created = Website.objects.get_or_create(domain = domain)
    site.update_favicon(icon)


@shared_task
def pull_from_pinboard():
    from .models import Bookmark

    if settings.PINBOARD_AUTH:
        pb = Pinboard(settings.PINBOARD_AUTH)
        recent = pb.posts.recent()

        for bookmark in recent['posts']:
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
                for tag in bookmark.tags:
                    db_bookmark.tags.add(tag)


@shared_task
def push_to_pinboard(pk):
    from .models import Bookmark

    bookmark = Bookmark.objects.get(pk=pk)
    pb = Pinboard(settings.PINBOARD_AUTH)
    pb.posts.add(
        url = bookmark.url,
        description = unicode(bookmark.title).encode('utf-8'),
        extended = unicode(bookmark.description).encode('utf-8'),
        tags = unicode(bookmark.tags_as_string()).encode('utf-8'),
    )
