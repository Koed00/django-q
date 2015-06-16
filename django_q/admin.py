from django.contrib import admin

# Register your models here.
from .models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = (
        u'name',
        'func',
        'started',
        'time_taken',
        'success'
    )
admin.site.register(Task, TaskAdmin)
