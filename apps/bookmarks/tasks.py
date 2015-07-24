from __future__ import absolute_import

from celery import shared_task



@shared_task
def update_bookmark_archive(pk):
    from .models import Bookmark

    bookmark = Bookmark.objects.get(pk=pk)
    bookmark.archives.create()
