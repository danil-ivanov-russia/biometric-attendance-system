import datetime
import uuid

from django.db import models
from django.utils import timezone
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


# Create your models here.
# class Attendee(AbstractUser):
#     patronymic = models.CharField(max_length=150, blank=True)
#
#     def get_full_name(self):
#         full_name = "%s %s %s" % (self.first_name, self.last_name, self.patronymic)
#         return full_name.strip()


class Biometrics(models.Model):
    # owner = models.ForeignKey(Attendee, on_delete=models.CASCADE)
    facial_data = models.BinaryField()


class Event(models.Model):
    name = models.CharField(max_length=200, blank=True)
    uuid = models.CharField(max_length=36, blank=True)
    datetime = models.DateTimeField()
    # attendees = models.ManyToManyField(Attendee)

    def __str__(self):
        return self.name

