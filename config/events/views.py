from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth import login

from .forms import EventForm, ImageForm, NewUserForm
from .models import Event
import uuid


# Create your views here.
class RegisterView(generic.FormView):
    template_name = 'events/register.html'
    form_class = NewUserForm


def create_user(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            #messages.success(request, "Registration successful.")
            return HttpResponseRedirect(reverse('events:new-event'))
            #return redirect("main:homepage")
        #messages.error(request, "Unsuccessful registration. Invalid information.")
    # form = NewUserForm()
    #return render(request=request, template_name="events/register.html", context={"register_form": form})
    return HttpResponseRedirect(reverse('events:register'))


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
    event = get_object_or_404(Event, slug=slug)
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            image_instance = form.instance
            image_datetime = image_instance.get_image_datetime()
            print(image_datetime)
            image_instance.delete()
            # return HttpResponseRedirect(reverse('events:attend', kwargs={"slug": event.slug}))
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
