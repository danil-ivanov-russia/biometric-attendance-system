from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .forms import EventForm, ImageForm
from .models import Event
import uuid


# Create your views here.
class NewEventView(generic.FormView):
    template_name = 'events/new-event.html'
    form_class = EventForm


def create_event(request):
    if request.method == 'POST':
        event = Event(slug=str(uuid.uuid4()), datetime=timezone.now())
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('events:qrcode', args=(event.pk,)))


class QRCodeView(generic.DetailView):
    model = Event
    template_name = 'events/qrcode.html'


def construct_attendance_page(request):
    slug = request.GET.get('slug', '')
    print(slug)
    event = get_object_or_404(Event, slug=slug)
    return HttpResponseRedirect(reverse('events:attend', args=(event.slug,)))


class AttendView(generic.DetailView):
    model = Event
    form_class = ImageForm
    template_name = 'events/attend.html'


def upload_attendance_photo(request, event_slug):
    #event = get_object_or_404(Event, slug=event_slug)
    print(event_slug)
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            print(form)
            #return HttpResponseRedirect(reverse('events:attend', kwargs={"slug": event.slug}))
    return HttpResponseRedirect(reverse('events:qrcode', args=(1,)))


def test(request, slug):
    if request.method == 'POST':
        print(slug)
    return HttpResponseRedirect(reverse('events:qrcode', args=(1,)))
        # form = ImageForm(request.POST, request.FILES)
        # if form.is_valid():
        #     print(form)
        #     #return HttpResponseRedirect(reverse('events:attend', kwargs={"slug": event.slug}))
        #     return HttpResponseRedirect(reverse('events:qrcode', args=(event.pk,)))