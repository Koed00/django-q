# Generated by Django 3.2.2 on 2021-05-11 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_q", "0013_task_attempt_count"),
    ]

    operations = [
        migrations.AddField(
            model_name="schedule",
            name="cluster",
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]
