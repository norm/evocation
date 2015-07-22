"""evocation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

from apps.bookmarks.views import (
    BookmarkCreate,
    BookmarkList,
    BookmarkUpdate,
    BookmarkTagUpdate,
    BookmarkView,
    TagsList,
    TaggedList,
)


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(
        r'^bookmark/$',
            BookmarkList.as_view(),
            name='bookmark-list',
    ),
    url(
        r'^bookmark/new$',
            BookmarkCreate.as_view(),
            name='bookmark-create',
    ),
    url(
        r'^bookmark/(?P<pk>\d+)/$',
            BookmarkView.as_view(),
            name='bookmark-detail',
    ),
    url(
        r'^bookmark/(?P<pk>\d+)/edit/$',
            BookmarkUpdate.as_view(),
            name='bookmark-update',
    ),
    url(
        r'^bookmark/(?P<pk>\d+)/edit/tags/$',
            BookmarkTagUpdate.as_view(),
            name='bookmark-tag-update',
    ),
    url(
        r'^tag/$',
            TagsList.as_view(),
            name='tags-list',
    ),
    url(
        r'^tag/(?P<slug>[A-Za-z0-9-]+)$',
            TaggedList.as_view(),
            name='tagged-list',
    ),
]
