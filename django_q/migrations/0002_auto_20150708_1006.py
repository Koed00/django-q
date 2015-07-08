# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_q', '0001_squashed_0003_auto_20150707_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='task',
            field=models.CharField(null=True, max_length=32, editable=False),
        ),
        migrations.AlterField(
            model_name='task',
            name='id',
            field=models.CharField(serialize=False, max_length=32, primary_key=True, editable=False),
        ),
    ]
