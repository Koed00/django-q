"""Admin module for Django."""
from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from django_q.conf import Conf, croniter
from django_q.models import Success, Failure, Schedule, OrmQ
from django_q.tasks import async_task


class TaskAdmin(admin.ModelAdmin):
    """model admin for success tasks."""

    list_display = ("name", "func", "started", "stopped", "time_taken", "group")

    def has_add_permission(self, request):
        """Don't allow adds."""
        return False

    def has_change_permission(self, request, obj=None):
        """Don't allow change unless DEBUG mode is on"""
        if not settings.DEBUG:
            return False
        return super(TaskAdmin, self).has_change_permission(request, obj=None)

    def has_delete_permission(self, request, obj=None):
        """Don't allow delete unless DEBUG mode is on"""
        if not settings.DEBUG:
            return False
        return super(TaskAdmin, self).has_delete_permission(request, obj=None)

    def get_queryset(self, request):
        """Only show successes."""
        qs = super(TaskAdmin, self).get_queryset(request)
        return qs.filter(success=True)

    search_fields = ("name", "func", "group")
    readonly_fields = []
    list_filter = ("group",)

    def get_readonly_fields(self, request, obj=None):
        """Set all fields readonly."""
        return list(self.readonly_fields) + [field.name for field in obj._meta.fields]


def retry_failed(FailAdmin, request, queryset):
    """Submit selected tasks back to the queue."""
    for task in queryset:
        async_task(task.func, *task.args or (), hook=task.hook, **task.kwargs or {})
        task.delete()


retry_failed.short_description = _("Resubmit selected tasks to queue")


class FailAdmin(admin.ModelAdmin):
    """model admin for failed tasks."""

    list_display = ("name", "func", "started", "stopped", "short_result")

    def has_add_permission(self, request):
        """Don't allow adds."""
        return False

    def has_change_permission(self, request, obj=None):
        """Don't allow change unless DEBUG mode is on"""
        if not settings.DEBUG:
            return False
        return super(FailAdmin, self).has_change_permission(request, obj=None)

    def has_delete_permission(self, request, obj=None):
        """Don't allow delete unless DEBUG mode is on"""
        if not settings.DEBUG:
            return False
        return super(FailAdmin, self).has_delete_permission(request, obj=None)

    actions = [retry_failed]
    search_fields = ("name", "func")
    list_filter = ("group",)
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        """Set all fields readonly."""
        return list(self.readonly_fields) + [field.name for field in obj._meta.fields]


class ScheduleAdmin(admin.ModelAdmin):
    """ model admin for schedules """

    list_display = (
        "id",
        "name",
        "func",
        "schedule_type",
        "repeats",
        "next_run",
        "last_run",
        "success",
    )

    # optional cron strings
    if not croniter:
        readonly_fields = ("cron",)

    list_filter = ("next_run", "schedule_type")
    search_fields = ("func",)
    list_display_links = ("id", "name")

    def has_add_permission(self, request):
        """Don't allow add unless DEBUG mode is on"""
        if not settings.DEBUG:
            return False
        return super(ScheduleAdmin, self).has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        """Don't allow change unless DEBUG mode is on"""
        if not settings.DEBUG:
            return False
        return super(ScheduleAdmin, self).has_change_permission(request, obj=None)

    def has_delete_permission(self, request, obj=None):
        """Don't allow delete unless DEBUG mode is on"""
        if not settings.DEBUG:
            return False
        return super(ScheduleAdmin, self).has_delete_permission(request, obj=None)


class QueueAdmin(admin.ModelAdmin):
    """  queue admin for ORM broker """

    list_display = ("id", "key", "task_id", "name", "func", "lock")

    def save_model(self, request, obj, form, change):
        obj.save(using=Conf.ORM)

    def delete_model(self, request, obj):
        obj.delete(using=Conf.ORM)

    def get_queryset(self, request):
        return super(QueueAdmin, self).get_queryset(request).using(Conf.ORM)

    def has_add_permission(self, request):
        """Don't allow adds."""
        return False
    
    list_filter = ("key",)

    def has_change_permission(self, request, obj=None):
        """Don't allow change unless DEBUG mode is on"""
        if not settings.DEBUG:
            return False
        return super(QueueAdmin, self).has_change_permission(request, obj=None)


admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Success, TaskAdmin)
admin.site.register(Failure, FailAdmin)

if Conf.ORM or Conf.TESTING:
    admin.site.register(OrmQ, QueueAdmin)
