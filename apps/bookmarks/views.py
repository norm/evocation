from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import Bookmark


class BookmarkView(DetailView):
    model = Bookmark


class BookmarkCreate(CreateView):
    model = Bookmark
    fields = ['url', 'title', 'description', 'tags']


class BookmarkUpdate(UpdateView):
    model = Bookmark
    fields = ['url', 'title', 'description', 'tags']


class BookmarkList(ListView):
    model = Bookmark
