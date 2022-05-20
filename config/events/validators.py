from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


# def validate_time_string(value):
#     if re.match(r"(?:[01]\d|2[0123]):(?:[012345]\d):(?:[012345]\d)", str(value)):
#         raise ValidationError(
#             _('%(value) is not a valid time string'),
#             params={'value': value},
#         )

