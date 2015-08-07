import json
import pytz
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from apps.bookmarks.models import Bookmark


class Command(BaseCommand):
    help = 'Import bookmarks from a Pinboard JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', nargs='+', type=open)

    def handle(self, *args, **options):
        val = URLValidator()
        for file in options['json_file']:
            bookmarks = json.load(file)
            for bookmark in bookmarks:
                try:
                    val(bookmark['href'])
                except (ValidationError, ValueError) as e:
                    print ' ** ', e, bookmark['href']
                    continue

                timestamp = datetime.strptime(bookmark['time'], "%Y-%m-%dT%H:%M:%SZ")
                timestamp = pytz.utc.localize(timestamp)

                db_bookmark, created = Bookmark.objects.get_or_create(
                    defaults = {
                        'title': bookmark['description'],
                        'description': bookmark['extended'],
                        'date_added': timestamp,
                        'origin': 2,
                    },
                    url = bookmark['href'],
                )
                if created:
                    db_bookmark.add_tags(bookmark['tags'])
