# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.REST_SURVEYS_SURVEY_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField()),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'swappable': 'REST_SURVEYS_SURVEY_MODEL',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('survey', models.ForeignKey(to=settings.REST_SURVEYS_SURVEY_MODEL)),
            ],
            options={
                'swappable': 'REST_SURVEYS_SURVEYRESPONSE_MODEL',
            },
            bases=(models.Model,),
        ),
    ]
