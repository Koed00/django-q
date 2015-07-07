# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import picklefield.fields


class Migration(migrations.Migration):

    replaces = [('django_q', '0001_initial'), ('django_q', '0002_auto_20150630_1624'), ('django_q', '0003_auto_20150707_1854')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('func', models.CharField(max_length=256, help_text='e.g. module.tasks.function')),
                ('hook', models.CharField(max_length=256, help_text='e.g. module.tasks.result_function', null=True, blank=True)),
                ('args', models.TextField(help_text="e.g. 1, 2, 'John'", null=True, blank=True)),
                ('kwargs', models.TextField(help_text="e.g. x=1, y=2, name='John'", null=True, blank=True)),
                ('schedule_type', models.CharField(max_length=1, choices=[('O', 'Once'), ('H', 'Hourly'), ('D', 'Daily'), ('W', 'Weekly'), ('M', 'Monthly'), ('Q', 'Quarterly'), ('Y', 'Yearly')], verbose_name='Schedule Type', default='O')),
                ('repeats', models.SmallIntegerField(verbose_name='Repeats', help_text='n = n times, -1 = forever', default=-1)),
                ('next_run', models.DateTimeField(null=True, verbose_name='Next Run', default=django.utils.timezone.now)),
                ('task', models.CharField(max_length=100, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'Scheduled task',
                'ordering': ['next_run'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100, editable=False)),
                ('func', models.CharField(max_length=256)),
                ('hook', models.CharField(max_length=256, null=True)),
                ('args', picklefield.fields.PickledObjectField(editable=False, null=True)),
                ('kwargs', picklefield.fields.PickledObjectField(editable=False, null=True)),
                ('result', picklefield.fields.PickledObjectField(editable=False, null=True)),
                ('started', models.DateTimeField(editable=False)),
                ('stopped', models.DateTimeField(editable=False)),
                ('success', models.BooleanField(editable=False, default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Failure',
            fields=[
            ],
            options={
                'verbose_name': 'Failed task',
                'proxy': True,
            },
            bases=('django_q.task',),
        ),
        migrations.CreateModel(
            name='Success',
            fields=[
            ],
            options={
                'verbose_name': 'Successful task',
                'proxy': True,
            },
            bases=('django_q.task',),
        ),
        migrations.AlterModelOptions(
            name='failure',
            options={'verbose_name': 'Failed task', 'verbose_name_plural': 'Failed tasks'},
        ),
        migrations.AlterModelOptions(
            name='schedule',
            options={'verbose_name': 'Scheduled task', 'ordering': ['next_run'], 'verbose_name_plural': 'Scheduled tasks'},
        ),
        migrations.AlterModelOptions(
            name='success',
            options={'verbose_name': 'Successful task', 'verbose_name_plural': 'Successful tasks'},
        ),
    ]
