# Register your models here.
from django.contrib import admin

from apps.APyme.models import Profile, User


class ProfileInLine(admin.StackedInline):
    model = Profile


class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileInLine, ]


admin.site.register(User, UserAdmin)
