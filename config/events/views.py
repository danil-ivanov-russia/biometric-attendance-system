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


# class AttendView(generic.DetailView):
#     model = Event
#     form_class = ImageForm
#     template_name = 'events/attend.html'


class AttendView(generic.edit.FormMixin, generic.DetailView):
    model = Event
    form_class = ImageForm
    initial = {'image': ''}
    template_name = 'events/attend.html'

    def get_context_data(self, **kwargs):
        context = super(generic.DetailView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context
    #
    # def post(self, request, *args, **kwargs):
    #     form = self.form_class(request.POST)
    #     #if form.is_valid():
    #         #return HttpResponseRedirect('/success/')
    #
    #     return render(request, self.template_name, {'form': form})


def upload_attendance_photo(request, slug):
    #event = get_object_or_404(Event, slug=event_slug)
    print(slug)
    event = get_object_or_404(Event, slug=slug)
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data.get('image')
            print(image)
            pass
            #return HttpResponseRedirect(reverse('events:attend', kwargs={"slug": event.slug}))
    return HttpResponseRedirect(reverse('events:qrcode', args=(19,)))


# def test(request, slug):
#     if request.method == 'POST':
#         print(slug)
#     return HttpResponseRedirect(reverse('events:qrcode', args=(1,)))
#         # form = ImageForm(request.POST, request.FILES)
#         # if form.is_valid():
#         #     print(form)
#         #     #return HttpResponseRedirect(reverse('events:attend', kwargs={"slug": event.slug}))
#         #     return HttpResponseRedirect(reverse('events:qrcode', args=(event.pk,)))