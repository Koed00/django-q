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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('func', models.CharField(max_length=256)),
                ('hook', models.CharField(blank=True, max_length=256, null=True)),
                ('args', models.CharField(blank=True, max_length=256, null=True)),
                ('kwargs', models.CharField(blank=True, max_length=256, null=True)),
                ('schedule_type', models.CharField(choices=[('O', 'Once'), ('H', 'Hourly'), ('D', 'Daily'), ('W', 'Weekly'), ('M', 'Monthly'), ('Q', 'Quarterly'), ('Y', 'Yearly')], max_length=1, verbose_name='Schedule Type', default='O')),
                ('repeats', models.SmallIntegerField(verbose_name='Repeats', default=-1)),
                ('next_run', models.DateTimeField(null=True, verbose_name='Next Run', default=django.utils.timezone.now)),
                ('task', models.CharField(editable=False, max_length=100, null=True)),
            ],
            options={
                'ordering': ['next_run'],
                'verbose_name': 'Scheduled task',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(editable=False, max_length=100)),
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
