from django.contrib import admin

from .models import Success, Failure


class TaskAdmin(admin.ModelAdmin):
    list_display = (
        u'name',
        'func',
        'started',
        'time_taken'
    )

    def has_add_permission(self, request, obj=None):
        """Don't allow adds"""
        return False

    def get_queryset(self, request):
        """Only show successes"""
        qs = super(TaskAdmin, self).get_queryset(request)
        return qs.filter(success=True)

    search_fields = ['name']
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields]


def retry_failed(FailAdmin, request, queryset):
    pass


retry_failed.short_description = "Resubmit selected tasks to Q"


class FailAdmin(admin.ModelAdmin):
    list_display = (
        u'name',
        'func',
        'started',
        'result'
    )
    actions = [retry_failed]
    search_fields = ['name']
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields]


admin.site.register(Success, TaskAdmin)
admin.site.register(Failure, FailAdmin)
