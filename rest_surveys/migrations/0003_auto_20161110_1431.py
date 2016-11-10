# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_surveys', '0002_auto_20161024_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='surveystep',
            name='title',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
