import re
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_token(value):
    if not re.match('[0-9]+:[-_a-zA-Z0-9]+', value):
        raise ValidationError(_("%(value)s is not a valid token"), params={'value': value})
