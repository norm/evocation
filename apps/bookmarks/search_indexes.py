from celery_haystack.indexes import CelerySearchIndex
from haystack import indexes

from .models import Bookmark


class BookmarkIndex(CelerySearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title')
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Bookmark
