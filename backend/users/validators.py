import re

from django.core.exceptions import ValidationError


def username_validator(username: str) -> str:
    pattern = re.compile(r'^[\w.@+-]+\Z')
    if pattern.match(username):
        return username
    raise ValidationError(
        message=(f'Некорректный username: {username}\n'
                 f'username должен соответствовать паттерну!'),
        code=400
    )
