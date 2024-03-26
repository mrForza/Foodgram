from typing import Any

from rest_framework.exceptions import ValidationError


def validate_field_existance(value: Any, erorr_message: str):
    if not value:
        raise ValidationError(
            detail=erorr_message,
            code=400
        )


def validate_repetetive_values(value: list, error_message: str):
    for i in range(0, len(value) - 1):
        for j in range(i + 1, len(value)):
            if value[i] == value[j]:
                raise ValidationError(
                    detail=error_message,
                    code=400
                )


def validate_amount(value: list, error_message: str):
    for item in value:
        if item.get('amount') < 1:
            raise ValidationError(
                detail=error_message,
                code=400
            )
