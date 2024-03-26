from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser, Subscription

EMPTY_MESSAGE = 'Незаполненное поле'


@admin.register(CustomUser)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'count_subscribers',
        'count_recipes'
    )
    list_filter = (
        'username',
        'email'
    )
    search_fields = (
        'username',
        'email'
    )
    ordering = ('username', )
    empty_value_display = EMPTY_MESSAGE

    def count_subscribers(self, obj):
        return obj.subscriber.count()

    def count_recipes(self, obj):
        return obj.recipes.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )
    list_filter = (
        'author__username',
        'user__username'
    )
    search_fields = (
        'author__username',
        'author__email',
        'user__username',
        'user__email'
    )
    empty_value_display = EMPTY_MESSAGE
