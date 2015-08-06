from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    YearArchiveView,
    MonthArchiveView,
    DayArchiveView,
    DeleteView,
)
from django.views.generic.detail import SingleObjectMixin

from .models import Bookmark
from taggit.models import Tag


class BookmarkView(DetailView):
    model = Bookmark


class BookmarkCreate(CreateView):
    model = Bookmark
    fields = ['url', 'title', 'description', 'tags']
    bookmark = None

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        errors = form.errors.as_data()

        # empty tag field is not an error
        no_tags = 'tags' not in form.cleaned_data
        if no_tags:
            form.cleaned_data.update({'tags': []})
            del form.errors['tags']
            del errors['tags']

        # check if no extra information was filled out
        no_other_info = (
            no_tags
            and not form.cleaned_data['description']
            and not form.cleaned_data['title']
        )

        if errors.keys() == ['url'] and errors['url'][0].code == 'unique':
            bookmark = Bookmark.objects.get(url=form.data['url'])
            if no_other_info:
                # go to existing bookmark if all you've posted is the url
                return HttpResponseRedirect(bookmark.get_absolute_url())
            else:
                # make existing bookmark available for use in the form error
                self.bookmark = bookmark

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(BookmarkCreate, self).get_context_data(**kwargs)
        context['bookmark'] = self.bookmark
        return context


class BookmarkUpdate(UpdateView):
    model = Bookmark
    fields = ['url', 'title', 'description', 'tags']


class BookmarkArchiveUpdate(UpdateView):
    model = Bookmark

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.update_archive()
        return HttpResponseRedirect(self.get_success_url())


class BookmarkDelete(DeleteView):
    model = Bookmark
    success_url = reverse_lazy('bookmark-list')


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
    paginate_by = 20


class BookmarkYearList(YearArchiveView):
    model = Bookmark
    date_field = 'date_added'
    make_object_list = True
    queryset = Bookmark.objects.all()
    paginate_by = 20


class BookmarkMonthList(MonthArchiveView):
    model = Bookmark
    date_field = 'date_added'
    make_object_list = True
    queryset = Bookmark.objects.all()
    month_format = '%m'
    paginate_by = 20


class BookmarkDayList(DayArchiveView):
    model = Bookmark
    date_field = 'date_added'
    make_object_list = True
    queryset = Bookmark.objects.all()
    month_format = '%m'
    paginate_by = 20


class TagsList(ListView):
    model = Tag
    paginate_by = 20


class TaggedList(SingleObjectMixin, ListView):
    template_name = 'taggit/tagged_list.html'
    paginate_by = 20

    def get_queryset(self):
        self.object = self.get_object(Tag.objects.all())
        return self.object.taggit_taggeditem_items.all()
