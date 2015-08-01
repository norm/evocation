from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


def homepage_redirect(request):
    return HttpResponseRedirect(reverse('bookmark-list'))
