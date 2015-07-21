from django.http import HttpResponseRedirect
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


class BookmarkTagUpdate(UpdateView):
    model = Bookmark
    fields = ['tags']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if not form.is_valid():
            return self.form_invalid(form)

        update_type = request.POST.get('update', None)
        if update_type == 'add':
            # add tag(s)
            self.object.add_tags(request.POST.get('tags', ''))
            return HttpResponseRedirect(self.get_success_url())
        elif update_type == 'remove':
            # remove tag
            self.object.remove_tag(request.POST.get('tags', ''))
            return HttpResponseRedirect(self.get_success_url())
        else:
            # replacing tags
            return self.form_valid(form)


class BookmarkList(ListView):
    model = Bookmark
