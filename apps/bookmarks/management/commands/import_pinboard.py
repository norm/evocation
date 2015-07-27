import json
import pytz
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from apps.bookmarks.models import Bookmark


class Command(BaseCommand):
    help = 'Import bookmarks from a Pinboard JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', nargs='+', type=open)

    def handle(self, *args, **options):
        for file in options['json_file']:
            bookmarks = json.load(file)
            for bookmark in bookmarks:
                timestamp = datetime.strptime(bookmark['time'], "%Y-%m-%dT%H:%M:%SZ")
                timestamp = pytz.utc.localize(timestamp)

                db_bookmark = Bookmark.objects.create(
                    url=bookmark['href'],
                    title=bookmark['description'],
                    description=bookmark['extended'],
                    date_added=timestamp,
                )
                db_bookmark.add_tags(bookmark['tags'])
