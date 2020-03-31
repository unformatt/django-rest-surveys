# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.REST_SURVEYS_SURVEY_MODEL),
        migrations.swappable_dependency(settings.REST_SURVEYS_SURVEYRESPONSE_MODEL),
        ('rest_surveys', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveyQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inline_ordering_position', models.IntegerField(null=True, blank=True)),
                ('title', models.TextField()),
                ('description', models.TextField(null=True, blank=True)),
                ('is_required', models.BooleanField(default=True)),
                ('format', models.PositiveSmallIntegerField(choices=[(0, 'Open Ended'), (1, 'Choose One'), (2, 'Choose Multiple')])),
            ],
            options={
                'ordering': ('inline_ordering_position',),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyQuestionResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('custom_text', models.TextField(null=True, blank=True)),
                ('question', models.ForeignKey(on_delete=models.deletion.CASCADE, to='rest_surveys.SurveyQuestion')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyQuestionResponseOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inline_ordering_position', models.IntegerField(null=True, blank=True)),
                ('question', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='question_response_options', to='rest_surveys.SurveyQuestion')),
            ],
            options={
                'ordering': ('inline_ordering_position',),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyResponseOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inline_ordering_position', models.IntegerField(null=True, blank=True)),
                ('title', models.TextField()),
                ('description', models.TextField(null=True, blank=True)),
                ('survey', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='steps', to=settings.REST_SURVEYS_SURVEY_MODEL)),
            ],
            options={
                'ordering': ('inline_ordering_position',),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='surveyquestionresponseoption',
            name='response_option',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='question_response_options', to='rest_surveys.SurveyResponseOption'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='surveyquestionresponse',
            name='response_option',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, blank=True, to='rest_surveys.SurveyResponseOption', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='surveyquestionresponse',
            name='survey_response',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='question_responses', to=settings.REST_SURVEYS_SURVEYRESPONSE_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='surveyquestion',
            name='response_options',
            field=models.ManyToManyField(to='rest_surveys.SurveyResponseOption', through='rest_surveys.SurveyQuestionResponseOption', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='surveyquestion',
            name='step',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='questions', to='rest_surveys.SurveyStep'),
            preserve_default=True,
        ),
    ]
