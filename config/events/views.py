import datetime
import uuid

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .forms import EventForm, ImageForm, NewUserForm
from .mixins import LoginRequiredMessageMixin
from .models import Event, Attendee, Biometrics


# Представление главной страницы
class IndexView(generic.TemplateView):
    template_name = 'events/index.html'


# Представление страницы регистрации
class RegisterView(generic.FormView):
    template_name = 'events/register.html'
    form_class = NewUserForm


# Представление запроса регистрации пользователя
def create_user(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно.")
            return HttpResponseRedirect(reverse('events:profile'))
        else:
            messages.error(request, "Что-то пошло не так.")
            return render(request, 'events/register.html', {"form": form})
    return HttpResponseRedirect(reverse('events:register'))


# Представление страницы авторизации
class LoginView(generic.FormView):
    template_name = 'events/login.html'
    form_class = AuthenticationForm


# Представление запроса авторизации пользователя
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
    return redirect(reverse('events:login'))


# Представление запроса выхода пользователя из системы
@login_required
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('events:index'))


# Представление страницы создания мероприятия
class NewEventView(LoginRequiredMessageMixin, generic.edit.FormMixin, generic.TemplateView):
    login_url = 'events:login'
    redirect_field_name = 'redirect_to'
    permission_denied_message = 'Для создание мероприятия требуется авторизация.'
    template_name = 'events/new-event.html'
    form_class = EventForm


# Представление запроса создания мероприятия
def create_event(request):
    if request.method == 'POST':
        event = Event(slug=str(uuid.uuid4()), datetime=timezone.now())
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            form.instance.attendees.add(request.user)
            form.instance.save()
            return HttpResponseRedirect(reverse('events:event', args=(event.pk,)))
        else:
            messages.error(request, "Неверные параметры мероприятия.")
            return render(request, 'events/new-event.html', {
                "form": form,
                "redirect_field_name": 'redirect_to',
                "login_url": 'events:login',
            })


# Представление страницы мероприятия
class EventView(generic.DetailView):
    model = Event
    template_name = 'events/event.html'


# Представление страницы деталей мероприятия
class EventDetailView(generic.DetailView):
    model = Event
    template_name = 'events/event-detail.html'


# Представление запроса загрузки JSON-файла с деталями мероприятия
def provide_json(request, pk):
    event = get_object_or_404(Event, pk=pk)
    response = HttpResponse(event.get_json(), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=event_' + str(event.id) + '.json'
    return response


# Представление страницы профиля пользователя
class ProfileView(LoginRequiredMixin, generic.edit.FormMixin, generic.TemplateView):
    form_class = ImageForm
    initial = {'image': ''}
    template_name = 'events/profile.html'


# Представление запроса загрузки фотографии пользователя для сохранения данных лица в системе
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


# Представление страницы подтверждения посещаемости
class AttendView(generic.edit.FormMixin, generic.DetailView):
    model = Event
    form_class = ImageForm
    initial = {'image': ''}
    template_name = 'events/attend.html'

    def get_context_data(self, **kwargs):
        context = super(generic.DetailView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context


# Представление запроса загрузки фотографии пользователя для подтверждения посещаемости
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
                if detected_person is not None:
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
    return HttpResponseRedirect(reverse('events:attend', args=(event.slug,)))


# Представление запроса удаления набора данных лица
def delete_biometrics(request, pk):
    biometrics = get_object_or_404(Biometrics, pk=pk)
    if request.user.is_authenticated and request.user == biometrics.owner:
        biometrics.delete()
    return HttpResponseRedirect(reverse('events:profile'))


# Представление запроса рендеринга списка посетителей мероприятия
def attendees_list(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'events/attendees.html', {"event": event})


# Представление запроса рендеринга QR-кода мероприятия
def qrcode(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'events/qrcode.html', {"event": event})
