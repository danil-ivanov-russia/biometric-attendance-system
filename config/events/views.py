import datetime
import uuid

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
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
            messages.success(request, "Регистрация прошла успешно.")
            return HttpResponseRedirect(reverse('events:profile'))
            # return redirect("main:homepage")
        else:
            messages.error(request, "Что-то пошло не так.")
            return render(request, 'events/register.html', {"form": form})
            # return HttpResponseRedirect(reverse('events:register'))
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
                messages.info(request, f"Вы вошли как {username}.")
                return redirect(reverse('events:profile'))
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
            return render(request, 'events/login.html', {"form": form})
        # messages.error(request, "Unsuccessful registration. Invalid information.")
    # form = NewUserForm()
    # return render(request=request, template_name="events/register.html", context={"register_form": form})
    return redirect(reverse('events:login'))
    # return redirect('events:login')


@login_required
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('events:index'))


class NewEventView(LoginRequiredMixin, generic.edit.FormMixin, generic.TemplateView):
    login_url = 'events:login'
    redirect_field_name = 'redirect_to'
    template_name = 'events/new-event.html'
    form_class = EventForm


def create_event(request):
    if request.method == 'POST':
        event = Event(slug=str(uuid.uuid4()), datetime=timezone.now())
        print(event.datetime)
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            form.instance.attendees.add(request.user)
            form.instance.save()
            return HttpResponseRedirect(reverse('events:event', args=(event.pk,)))
        else:
            # return redirect(reverse('events:new-event'))
            messages.error(request, "Неверные параметры мероприятия.")
            return render(request, 'events/new-event.html', {
                "form": form,
                "redirect_field_name": 'redirect_to',
                "login_url": 'events:login',
            })


class EventView(generic.DetailView):
    model = Event
    template_name = 'events/event.html'


class EventDetailView(generic.DetailView):
    model = Event
    template_name = 'events/event-detail.html'


def provide_json(request, pk):
    event = get_object_or_404(Event, pk=pk)
    response = HttpResponse(event.get_json(), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=event_' + str(event.id) + '.json'
    return response


class ProfileView(LoginRequiredMixin, generic.edit.FormMixin, generic.TemplateView):
    form_class = ImageForm
    initial = {'image': ''}
    template_name = 'events/profile.html'


def upload_face_data_photo(request, pk):
    user = get_object_or_404(Attendee, pk=pk)
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            image_instance = form.instance
            face_encoding = image_instance.get_face_encoding()
            image_instance.delete()
            if face_encoding is not None:
                biometrics = Biometrics(
                    owner=user,
                    face_encoding=Biometrics.convert_encoding_to_binary(face_encoding)
                )
                biometrics.save()
            else:
                messages.error(request,
                               "Лицо на фотографии не обнаружено или был загружен неподходящий файл, попробуйте ещё раз.")
        else:
            messages.error(request, "Загружен неподходящий файл.")
    return HttpResponseRedirect(reverse('events:profile'))


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
            face_encoding = image_instance.get_face_encoding()
            image_instance.delete()
            if face_encoding is not None and \
                    (event.datetime - datetime.timedelta(minutes=1)
                     <= image_datetime
                     <= event.datetime + event.get_timer_interval()):
                detected_person = Biometrics.find_biometrics_by_encoding(face_encoding)
                # print(detected_person)
                if detected_person is not None:
                    # print(detected_person.get_full_name())
                    event.attendees.add(detected_person)
                    event.save()
                    messages.success(request, "Вы были распознаны как " + detected_person.get_full_name() + ".")
                    return HttpResponseRedirect(reverse('events:event-detail', args=(event.pk,)))
                else:
                    messages.error(request, "Не найдено совпадений с известными лицами пользователей.")
            else:
                messages.error(request, "Лицо на фотографии не обнаружено или был загружен неподходящий файл.")
        else:
            messages.error(request, "Загружен неподходящий файл.")
            # return HttpResponseRedirect(reverse('events:attend', kwargs={"slug": event.slug}))
    return HttpResponseRedirect(reverse('events:attend', args=(event.slug,)))


def delete_biometrics(request, pk):
    biometrics = get_object_or_404(Biometrics, pk=pk)
    if request.user.is_authenticated and request.user == biometrics.owner:
        biometrics.delete()
    return HttpResponseRedirect(reverse('events:profile'))


def attendees_list(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'events/attendees.html', {"event": event})


def qrcode(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'events/qrcode.html', {"event": event})
