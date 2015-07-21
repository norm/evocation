from django.db import models
from django.utils import timezone

from taggit.managers import TaggableManager


class Bookmark(models.Model):
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=1024, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    tags = TaggableManager()

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return self.url

    class Meta:
        ordering = ["-date_added"]
