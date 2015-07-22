from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

from taggit.managers import TaggableManager
from taggit.utils import parse_tags


class Bookmark(models.Model):
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=1024, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    tags = TaggableManager()

    def add_tag(self, tag):
        self.tags.add(tag)
        self.save()

    def add_tags(self, tags_string):
        for tag in parse_tags(tags_string):
            self.add_tag(tag)

    def remove_tag(self, tag):
        self.tags.remove(tag)
        self.save()

    def get_absolute_url(self):
        return reverse('bookmark-detail', kwargs={'pk': self.pk})

    def name(self):
        return self.__unicode__()

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return self.url

    class Meta:
        ordering = ["-date_added"]
