# Generated by Django 3.2.2 on 2021-05-11 05:59

from django.db import migrations, connection
from django_q.models import Schedule


class Migration(migrations.Migration):

    dependencies = [
        ('django_q', '0014_schedule_cluster'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name="schedule",
            index_together={("next_run", "repeats", "cluster")},
        ),
    ]
