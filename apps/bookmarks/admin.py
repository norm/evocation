from django.contrib import admin

from .models import Bookmark, BookmarkArchive

admin.site.register(Bookmark)
admin.site.register(BookmarkArchive)
