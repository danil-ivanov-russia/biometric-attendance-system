from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .forms import EventForm
from .models import Event
import uuid


# Create your views here.
class NewEventView(generic.FormView):
    template_name = 'events/new-event.html'
    form_class = EventForm
    #context = {'form':form}
    #return render(request, template_name, context)


def create_event(request):
    print("GOT HERE")
    if request.method == 'POST':
        #print(request.POST)
        event = Event(uuid=str(uuid.uuid4()), datetime=timezone.now())
        print(event.uuid)
        form = EventForm(request.POST, instance=event)
        #form = EventForm(request.POST, initial={'uuid': str(uuid.uuid4())})
        if form.is_valid():
            #print(form)
            form.save()
            return HttpResponseRedirect(reverse('events:qrcode', args=(event.pk,)))


class QRCodeView(generic.DetailView):
    model = Event
    template_name = 'events/qrcode.html'


class AttendView(generic.DetailView):
    model = Event
    template_name = 'events/attend.html'
