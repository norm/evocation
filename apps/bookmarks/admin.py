from django.contrib import admin

from .models import Bookmark, BookmarkArchive, Website

admin.site.register(Bookmark)
admin.site.register(BookmarkArchive)
admin.site.register(Website)
