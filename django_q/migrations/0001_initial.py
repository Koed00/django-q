# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('func', models.CharField(help_text='e.g. module.tasks.function', max_length=256)),
                ('hook', models.CharField(blank=True, help_text='e.g. module.tasks.result_function', max_length=256, null=True)),
                ('args', models.CharField(blank=True, help_text="e.g. 1, 2, 'John'", max_length=256, null=True)),
                ('kwargs', models.CharField(blank=True, help_text="e.g. x=1, y=2, name='John'", max_length=256, null=True)),
                ('schedule_type', models.CharField(choices=[('O', 'Once'), ('H', 'Hourly'), ('D', 'Daily'), ('W', 'Weekly'), ('M', 'Monthly'), ('Q', 'Quarterly'), ('Y', 'Yearly')], default='O', verbose_name='Schedule Type', max_length=1)),
                ('repeats', models.SmallIntegerField(help_text='n = n times, -1 = forever', default=-1, verbose_name='Repeats')),
                ('next_run', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Next Run')),
                ('task', models.CharField(editable=False, max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Scheduled task',
                'ordering': ['next_run'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100, editable=False)),
                ('func', models.CharField(max_length=256)),
                ('hook', models.CharField(max_length=256, null=True)),
                ('args', picklefield.fields.PickledObjectField(editable=False)),
                ('kwargs', picklefield.fields.PickledObjectField(editable=False)),
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
    ]
