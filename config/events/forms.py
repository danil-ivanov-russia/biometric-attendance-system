from django.forms import ModelForm
from .models import Event, FaceImage


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['name']


class ImageForm(ModelForm):
    class Meta:
        model = FaceImage
        fields = ['image']
