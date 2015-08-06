import json
import pytz
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import pinboard

from apps.bookmarks.models import Bookmark
from apps.bookmarks.tasks import pull_from_pinboard


class Command(BaseCommand):
    help = 'Fetch recent bookmarks from Pinboard'

    def handle(self, *args, **options):
        if settings.PINBOARD_AUTH is None:
            raise CommandError('PINBOARD_AUTH not set')
        pull_from_pinboard()

