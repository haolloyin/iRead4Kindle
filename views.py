# coding=utf8


from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

def home(request):
    return render_to_response('home.html',
            context_instance=RequestContext(request))



