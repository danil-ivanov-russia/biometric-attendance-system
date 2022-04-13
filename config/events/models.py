from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Attendee(AbstractUser):
    patronymic = models.CharField(max_length=150, blank=True)

    def get_full_name(self):
        full_name = "%s %s %s" % (self.first_name, self.last_name, self.patronymic)
        return full_name.strip()


class Biometrics(models.Model):
    owner = models.ForeignKey(Attendee, on_delete=models.CASCADE)
    facial_data = models.BinaryField()
