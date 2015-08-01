from .models import Bookmark
from taggit.models import Tag


def total(request):
    context = {
        'total_bookmarks': Bookmark.objects.count(),
        'all_bookmarks': Bookmark.objects.all(),
        'all_tags': Tag.objects.all().order_by('name'),
    }

    return context
