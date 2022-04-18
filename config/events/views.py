from django.shortcuts import render
from django.views import generic
from django.utils import timezone
from .forms import EventForm
from .models import Event
import uuid


# Create your views here.
# class CreateEventView(generic.FormView):
def create_event(request):
    form = EventForm()

    if request.method == 'POST':
        #print(request.POST)
        event = Event(uuid=str(uuid.uuid4()), datetime=timezone.now())
        print(event.uuid)
        form = EventForm(request.POST, instance=event)
        #form = EventForm(request.POST, initial={'uuid': str(uuid.uuid4())})
        if form.is_valid():
            #print(form)
            form.save()

    context = {'form':form}
    template_name = 'events/create.html'

    return render(request, template_name, context)


class QRCodeView(generic.DetailView):
    model = Event
    template_name = 'events/qrcode.html'


# class AttendView(generic.DetailView):
#     model = Event
#     template_name = 'events/attend.html'
