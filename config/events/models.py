import datetime
import face_recognition
import numpy as np

from django.conf import settings
from django.db import models
from django.http import request
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from PIL.ExifTags import TAGS
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Attendee(AbstractUser):
    patronymic = models.CharField(max_length=150, blank=True, verbose_name="Отчество")

    def get_full_name(self):
        full_name = "%s %s %s" % (self.first_name, self.last_name, self.patronymic)
        return full_name.strip()


class Biometrics(models.Model):
    owner = models.ForeignKey(Attendee, on_delete=models.CASCADE)
    face_encoding = models.BinaryField()


class Event(models.Model):
    name = models.CharField(max_length=200, blank=True)
    slug = models.CharField(max_length=36, blank=True)
    datetime = models.DateTimeField()
    # attendees = models.ManyToManyField(Attendee)

    def __str__(self):
        return self.name

    def get_attendance_url(self):
        return reverse('events:attend', kwargs={"slug": self.slug})


class FaceImage(models.Model):
    image = models.ImageField()

    def delete(self, using=None, keep_parents=False):
        self.image.delete(save=False)
        super().delete()

    def get_image_datetime(self):
        raw_image = Image.open(self.image.path)
        exif_data = raw_image.getexif()
        datetime_object = None
        for tag_id in exif_data:
            tag = TAGS.get(tag_id, tag_id)
            if tag == "DateTime":
                data = exif_data.get(tag_id)
                if isinstance(data, bytes):
                    data = data.decode()
                datetime_object = datetime.datetime.strptime(data, '%Y:%m:%d %H:%M:%S')
                break
        return datetime_object

    def get_face_encoding(self):
        raw_image = Image.open(self.image.path)
        face_encoding = None
        for i in range(-1, 2):
            rotated_image = raw_image.rotate(90 * i, expand=True)
            #rotated_image.save(self.image.path)
            current_image = np.array(rotated_image)
            #face_recognition.load_image_file(self.image.path)
            face_encodings = face_recognition.face_encodings(current_image)
            if face_encodings:
                print(i)
                face_encoding = face_encodings[0]
                break
        return face_encoding

