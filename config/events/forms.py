from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Event, FaceImage, Attendee


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['name']


class ImageForm(ModelForm):
    class Meta:
        model = FaceImage
        fields = ['image']


class NewUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['last_name'].required = True

    class Meta:
        model = Attendee
        fields = ("username", "last_name", "first_name", "patronymic", "email", "password1", "password2")
