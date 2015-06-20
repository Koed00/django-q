# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('func', models.CharField(max_length=256)),
                ('hook', models.CharField(max_length=256, null=True)),
                ('args', picklefield.fields.PickledObjectField(editable=False)),
                ('kwargs', picklefield.fields.PickledObjectField(editable=False)),
                ('result', picklefield.fields.PickledObjectField(editable=False)),
                ('started', models.DateTimeField()),
                ('stopped', models.DateTimeField()),
                ('success', models.BooleanField(default=True)),
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
