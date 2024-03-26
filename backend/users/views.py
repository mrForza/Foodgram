import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from api.serializers import CustomUserRetrieveSerializer, TokenLoginSerializer
from users.models import ExpiredToken


@login_required
@require_GET
def check_profile(requset: HttpRequest):
    if requset.headers.get('authorization') is not None:
        if requset.user.is_authenticated:
            return JsonResponse(
                data=CustomUserRetrieveSerializer(
                    instance=requset.user
                ).data,
                status=200
            )
    return JsonResponse(
        data={},
        status=401
    )


@login_required
def change_password_view(request: HttpRequest):
    if request.user.is_authenticated:
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        current_password = body_data.get('current_password')
        new_password = body_data.get('new_password')

        if request.user.check_password(current_password):
            request.user.set_password(new_password)
            request.user.save()
            return HttpResponse('', status=204)
        return JsonResponse(
            data={'detail': 'Ошибка при смене пароля'},
            status=400
        )
    return JsonResponse(
        data={'detail': 'Учетные данные не были предоставлены.'},
        status=401
    )


@require_POST
def login_view(request: HttpRequest):
    body_unicode = request.body.decode('utf-8')
    body_data = json.loads(body_unicode)

    email = body_data.get('email', 'default')
    password = body_data.get('password', 'default')
    serializer = TokenLoginSerializer(
        data={
            'email': email,
            'password': password
        }
    )

    try:
        serializer.is_valid(raise_exception=True)
        auth_token = serializer.validated_data.get('access')
        if auth_token is not None:
            user = authenticate(
                request=request,
                username=email, password=password
            )
            if user is not None:
                login(request, user)
                return JsonResponse(
                    data={'auth_token': auth_token},
                    status=200
                )
    except ValidationError:
        return JsonResponse(
            data={'details': 'Некорректные данные для входа!'},
            status=400
        )
    except AuthenticationFailed:
        return JsonResponse(
            data={'details': 'Не найден пользователь с такими данными!'},
            status=400
        )


@login_required
def logout_view(request: HttpRequest):
    auth_token = request.headers.get('Authorization').split(' ')[-1]
    if auth_token is not None:
        ExpiredToken.objects.create(
            value=auth_token,
            user=request.user
        )
        logout(request)
        return HttpResponse('', status=204)
    return HttpResponse(
        content='No token!',
        status=400
    )
