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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('func', models.CharField(max_length=256)),
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
                'proxy': True,
            },
            bases=('django_q.task',),
        ),
        migrations.CreateModel(
            name='Success',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('django_q.task',),
        ),
    ]
