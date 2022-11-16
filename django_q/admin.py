"""Admin module for Django."""
from django.contrib import admin
from django.db.models.expressions import OuterRef, Subquery
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from django_q.conf import Conf, croniter
from django_q.models import Failure, OrmQ, Schedule, Success, Task
from django_q.tasks import async_task


class TaskAdmin(admin.ModelAdmin):
    """model admin for success tasks."""

    list_display = ("name", "group", "func", "started", "stopped", "time_taken")

    def has_add_permission(self, request):
        """Don't allow adds."""
        return False

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

    list_display = ("name", "group", "func", "started", "stopped", "short_result")

    def has_add_permission(self, request):
        """Don't allow adds."""
        return False

    actions = [retry_failed]
    search_fields = ("name", "func", "group")
    list_filter = ("group",)
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        """Set all fields readonly."""
        return list(self.readonly_fields) + [field.name for field in obj._meta.fields]


class ScheduleAdmin(admin.ModelAdmin):
    """model admin for schedules"""

    list_display = (
        "id",
        "name",
        "func",
        "schedule_type",
        "repeats",
        "cluster",
        "next_run",
        "get_last_run",
        "get_success",
    )

    # optional cron strings
    if not croniter:
        readonly_fields = ("cron",)

    list_filter = ("next_run", "schedule_type", "cluster")
    search_fields = (
        "name",
        "func",
    )
    list_display_links = ("id", "name")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        task_query = Task.objects.filter(id=OuterRef("task")).values(
            "id", "name", "success"
        )
        qs = qs.annotate(
            task_id=Subquery(task_query.values("id")),
            task_name=Subquery(task_query.values("name")),
            task_success=Subquery(task_query.values("success")),
        )
        return qs

    def get_success(self, obj):
        return obj.task_success

    get_success.boolean = True
    get_success.short_description = _("success")

    def get_last_run(self, obj):
        if obj.task_name is not None:
            if obj.task_success:
                url = reverse("admin:django_q_success_change", args=(obj.task_id,))
            else:
                url = reverse("admin:django_q_failure_change", args=(obj.task_id,))
            return format_html(f'<a href="{url}">[{obj.task_name}]</a>')
        return None

    get_last_run.allow_tags = True
    get_last_run.short_description = _("last_run")


class QueueAdmin(admin.ModelAdmin):
    """queue admin for ORM broker"""

    list_display = ("id", "key", "name", "group", "func", "lock", "task_id")

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


admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Success, TaskAdmin)
admin.site.register(Failure, FailAdmin)

if Conf.ORM or Conf.TESTING:
    admin.site.register(OrmQ, QueueAdmin)
