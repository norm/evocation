import json
import pytz
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import pinboard

from apps.bookmarks.models import Bookmark


class Command(BaseCommand):
    help = 'Fetch recent bookmarks from Pinboard'

    def handle(self, *args, **options):
        if settings.PINBOARD_AUTH is None:
            raise CommandError('PINBOARD_AUTH not set')

        pb = pinboard.Pinboard(settings.PINBOARD_AUTH)
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
                },
                url = bookmark.url,
            )
            if created:
                for tag in bookmark.tags:
                    db_bookmark.tags.add(tag)
