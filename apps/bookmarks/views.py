from django.views.generic import DetailView, ListView

from .models import Bookmark


class BookmarkView(DetailView):
    model = Bookmark


class BookmarkList(ListView):
    model = Bookmark
