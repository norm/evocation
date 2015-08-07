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
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from apps.bookmarks.views import (
    BookmarkCreate,
    BookmarkList,
    BookmarkUpdate,
    BookmarkTagUpdate,
    BookmarkView,
    BookmarkYearList,
    BookmarkMonthList,
    BookmarkDayList,
    TagsList,
    TaggedList,
    BookmarkArchiveUpdate,
    BookmarkDelete,
)
from evocation.views import homepage_redirect


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(
        r'^$',
            homepage_redirect
    ),

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
        r'^bookmark/(?P<year>[0-9]{4})/$',
            BookmarkYearList.as_view(),
            name='bookmark-by-year',
    ),
    url(
        r'^bookmark/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
            BookmarkMonthList.as_view(),
            name='bookmark-by-month',
    ),
    url(
        r'^bookmark/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/$',
            BookmarkDayList.as_view(),
            name='bookmark-by-day',
    ),
    url(
        r'^bookmark/id/(?P<pk>\d+)/$',
            BookmarkView.as_view(),
            name='bookmark-detail',
    ),
    url(
        r'^bookmark/id/(?P<pk>\d+)/edit/$',
            BookmarkUpdate.as_view(),
            name='bookmark-update',
    ),
    url(
        r'^bookmark/id/(?P<pk>\d+)/delete/$',
            BookmarkDelete.as_view(),
            name='bookmark-delete',
    ),
    url(
        r'^bookmark/id/(?P<pk>\d+)/rearchive/$',
            BookmarkArchiveUpdate.as_view(),
            name='bookmark-rearchive',
    ),
    url(
        r'^bookmark/id/(?P<pk>\d+)/edit/tags/$',
            BookmarkTagUpdate.as_view(),
            name='bookmark-tag-update',
    ),
    url(
        r'^tag/$',
            TagsList.as_view(),
            name='tags-list',
    ),
    url(
        r'^tag/(?P<slug>[A-Za-z0-9_-]+)$',
            TaggedList.as_view(),
            name='tagged-list',
    ),

    url(r'^search/', include('haystack.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)