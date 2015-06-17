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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('func', models.CharField(max_length=256)),
                ('task', picklefield.fields.PickledObjectField(editable=False)),
                ('result', picklefield.fields.PickledObjectField(editable=False)),
                ('started', models.DateTimeField()),
                ('stopped', models.DateTimeField()),
                ('success', models.BooleanField(default=True)),
            ],
        ),
    ]
