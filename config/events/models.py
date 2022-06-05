import datetime as dt
import io
import json

import face_recognition
import numpy as np

from django.db import models
from django.forms import model_to_dict
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from PIL.ExifTags import TAGS
from django.contrib.auth.models import AbstractUser


# Модель пользователя/посетителя мероприятия
class Attendee(AbstractUser):
    patronymic = models.CharField(max_length=150, blank=True, verbose_name="Отчество")

    # Получить полное ФИО пользователя
    def get_full_name(self):
        full_name = "%s %s %s" % (self.last_name, self.first_name, self.patronymic)
        return full_name.strip()

    # Получить список посещённых пользователем мероприятий
    def get_attended_events(self):
        events_list = Event.objects.filter(attendees=self)
        if not events_list:
            return None
        else:
            return reversed(events_list)

    # Получить список наборов биометрических данных пользователя
    def get_biometrics(self):
        biometrics_list = Biometrics.objects.filter(owner=self)
        return reversed(biometrics_list)


# Модель набора биометрических данных лица
class Biometrics(models.Model):
    owner = models.ForeignKey(Attendee, on_delete=models.CASCADE)
    face_encoding = models.BinaryField()

    # Перевести массив NumPy в двоичный вид
    @staticmethod
    def convert_encoding_to_binary(encoding):
        out = io.BytesIO()
        np.save(out, encoding)
        out.seek(0)
        return out.read()

    # Перевести данные в двоичном виде в массив NumPy
    @staticmethod
    def convert_binary_to_encoding(binary):
        out = io.BytesIO(binary)
        out.seek(0)
        return np.load(out)

    # Определить личность пользователя по набору данных
    @staticmethod
    def find_biometrics_by_encoding(encoding):
        all_biometrics = Biometrics.objects.all()
        all_encodings = []
        for biometrics in all_biometrics:
            current_encoding = Biometrics.convert_binary_to_encoding(biometrics.face_encoding)
            all_encodings.append(current_encoding)
        matches = face_recognition.compare_faces(all_encodings, encoding)
        face_distances = face_recognition.face_distance(all_encodings, encoding)
        if not face_distances.any():
            return None
        else:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                return all_biometrics[int(best_match_index)].owner
            else:
                return None


# Модель мероприятия, для которого проводится контроль посещаемости
class Event(models.Model):
    name = models.CharField(max_length=200, blank=True, verbose_name="Название")
    slug = models.CharField(max_length=36, blank=True)
    datetime = models.DateTimeField()
    timer = models.TimeField(default=dt.time(0, 5), verbose_name="Таймер")
    attendees = models.ManyToManyField(Attendee)

    def __str__(self):
        return self.name

    # Получить ссылку на страницу подтверждения посещаемости
    def get_attendance_url(self):
        return reverse('events:attend', kwargs={"slug": self.slug})

    # Получить длительность подтверждения посещаемости
    def get_timer_interval(self):
        return dt.timedelta(hours=self.timer.hour, minutes=self.timer.minute, seconds=self.timer.second)

    # Получить оставшееся на подтверждение посещаемости время
    def get_timer_remaining(self):
        remaining_time = self.get_timer_interval() - (timezone.now() - self.datetime)
        result = str(remaining_time).split('.')[0]
        if remaining_time < dt.timedelta(hours=0, minutes=0, seconds=0):
            result = False
        return result

    # Получить JSON-файл с деталями мероприятия
    def get_json(self):
        temp_dictionary = model_to_dict(self, fields=['id', 'name', 'datetime', 'attendees'])
        temp_dictionary['attendees'] = list(self.attendees.all().values(
            'id', 'username', 'first_name', 'patronymic', 'last_name', 'email'
        ))
        json_file = json.dumps(temp_dictionary, default=str, ensure_ascii=False)
        return json_file


# Модель фотографии лица
class FaceImage(models.Model):
    image = models.ImageField(verbose_name="Фото", help_text="Сделайте фотографию своего лица анфас. Лицо должно занимать 80% изображения.")

    # Удалить сущность фотографии лица из системы и файл фотографии с диска
    def delete(self, using=None, keep_parents=False):
        self.image.delete(save=False)
        super().delete()

    # Получить время создания фотографии из метаданных
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
                datetime_object = dt.datetime.strptime(data, '%Y:%m:%d %H:%M:%S')
                break
        return datetime_object

    # Получить набор данных лица из фотографии
    def get_face_encoding(self):
        face_encoding = None
        try:
            raw_image = Image.open(self.image.path)
            for i in range(-1, 2):
                rotated_image = raw_image.rotate(90 * i, expand=True)
                current_image = np.array(rotated_image)
                face_encodings = face_recognition.face_encodings(current_image)
                if face_encodings:
                    face_encoding = face_encodings[0]
                    break
        finally:
            return face_encoding
