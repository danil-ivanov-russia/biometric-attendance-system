from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Event, FaceImage, Attendee


class EventForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['timer'].required = True

    class Meta:
        model = Event
        fields = ('name', 'timer', )


class ImageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = True

    class Meta:
        model = FaceImage
        fields = ['image']


class NewUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['last_name'].required = True
        self.fields['first_name'].required = True

    class Meta:
        model = Attendee
        fields = ("username",  "email", "password1", "password2", "last_name", "first_name", "patronymic", )
