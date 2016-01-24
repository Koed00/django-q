# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_q', '0007_ormq'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='broker_name',
            field=models.CharField(max_length=100),
        ),
    ]
