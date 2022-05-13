import datetime
import uuid

from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import generic, View
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .forms import EventForm, ImageForm, NewUserForm
from .models import Event, Attendee, Biometrics


# Create your views here.
class IndexView(generic.TemplateView):
    template_name = 'events/index.html'


class RegisterView(generic.FormView):
    template_name = 'events/register.html'
    form_class = NewUserForm


def create_user(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # messages.success(request, "Registration successful.")
            return HttpResponseRedirect(reverse('events:profile'))
            # return redirect("main:homepage")
        # messages.error(request, "Unsuccessful registration. Invalid information.")
    # form = NewUserForm()
    # return render(request=request, template_name="events/register.html", context={"register_form": form})
    return HttpResponseRedirect(reverse('events:register'))


class LoginView(generic.FormView):
    template_name = 'events/login.html'
    form_class = AuthenticationForm


def authenticate_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return HttpResponseRedirect(reverse('events:profile'))
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
            # return redirect("main:homepage")
        # messages.error(request, "Unsuccessful registration. Invalid information.")
    # form = NewUserForm()
    # return render(request=request, template_name="events/register.html", context={"register_form": form})
    return HttpResponseRedirect(reverse('events:login'))


@login_required
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('events:index'))


class NewEventView(LoginRequiredMixin, generic.edit.FormMixin, generic.TemplateView):
    login_url = 'events:login'
    redirect_field_name = 'redirect_to'
    template_name = 'events/new-event.html'
    form_class = EventForm

    # def get_context_data(self, **kwargs):
    #     context = self.get_context_data()
    #     context['form'] = self.get_form()
    #     return context


# class NewEventView(generic.FormView):
#     template_name = 'events/new-event.html'
#     form_class = EventForm


def create_event(request):
    if request.method == 'POST':
        event = Event(slug=str(uuid.uuid4()), datetime=timezone.now())
        print(event.datetime)
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
class ProfileView(LoginRequiredMixin, generic.edit.FormMixin, generic.TemplateView):
    #model = Attendee
    form_class = ImageForm
    initial = {'image': ''}
    template_name = 'events/profile.html'

    # def get_context_data(self, **kwargs):
    #     context = super(generic.DetailView, self).get_context_data(**kwargs)
    #     context['form'] = self.get_form()
    #     return context


def upload_face_data_photo(request, pk):
    user = get_object_or_404(Attendee, pk=pk)
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            image_instance = form.instance
            face_encoding = image_instance.get_face_encoding()
            print(face_encoding)
            if face_encoding is not None:
                biometrics = Biometrics(
                    owner=user,
                    face_encoding=Biometrics.convert_encoding_to_binary(face_encoding)
                )
                biometrics.save()
                # print(Biometrics.convert_binary_to_encoding(biometrics.face_encoding))
            image_instance.delete()
    return HttpResponseRedirect(reverse('events:profile', args=(user.pk,)))


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
            print(event.datetime - datetime.timedelta(minutes=1))
            print(image_datetime)
            print(event.datetime + datetime.timedelta(minutes=10))
            face_encoding = image_instance.get_face_encoding()
            print(face_encoding)
            if face_encoding is not None and \
                    (event.datetime - datetime.timedelta(minutes=1)
                     <= image_datetime
                     <= event.datetime + datetime.timedelta(minutes=10)):
                detected_person = Biometrics.find_biometrics_by_encoding(face_encoding)
                print(detected_person)
                if detected_person is not None:
                    print(detected_person.get_full_name())
                    event.attendees.add(detected_person)
                    event.save()
            image_instance.delete()
            # return HttpResponseRedirect(reverse('events:attend', kwargs={"slug": event.slug}))
    return HttpResponseRedirect(reverse('events:qrcode', args=(event.pk,)))


def attendees_list(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'events/attendees.html', {"event": event})
