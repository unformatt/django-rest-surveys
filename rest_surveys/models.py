from __future__ import unicode_literals

from django.db import models

import swapper

from inline_ordering.models import Orderable
# NOTE: Until we make inline_ordering optional, require users to add
# 'inline_ordering' to their INSTALLED_APPS.
# See: http://stackoverflow.com/a/30472909/1658458


class AbstractSurvey(models.Model):
    title = models.TextField()
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class Survey(AbstractSurvey):
    class Meta:
        swappable = swapper.swappable_setting('rest_surveys', 'Survey')


class SurveyStep(Orderable):
    survey = models.ForeignKey(swapper.get_model_name('rest_surveys', 'Survey'),
                               related_name='steps')
    title = models.TextField()
    description = models.TextField(null=True, blank=True)


class SurveyQuestion(Orderable):
    step = models.ForeignKey('rest_surveys.SurveyStep',
                             related_name='questions')
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    is_required = models.BooleanField(default=True)
    OPEN_ENDED = 0
    CHOOSE_ONE = 1
    CHOOSE_MULTIPLE = 2
    FORMAT_CHOICES = (
        (OPEN_ENDED, 'Open Ended'),
        (CHOOSE_ONE, 'Choose One'),
        (CHOOSE_MULTIPLE, 'Choose Multiple'),
    )
    format = models.PositiveSmallIntegerField(
            choices=FORMAT_CHOICES)
    response_options = models.ManyToManyField(
            'rest_surveys.SurveyResponseOption',
            blank=True,
            through='rest_surveys.SurveyQuestionResponseOption')


class SurveyResponseOption(models.Model):
    text = models.TextField()


class SurveyQuestionResponseOption(Orderable):
    question = models.ForeignKey('rest_surveys.SurveyQuestion',
                                 related_name='question_response_options')
    response_option = models.ForeignKey('rest_surveys.SurveyResponseOption',
                                        related_name='question_response_options')

class AbstractSurveyResponse(models.Model):
    survey = models.ForeignKey(swapper.get_model_name('rest_surveys', 'Survey'))
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class SurveyResponse(AbstractSurveyResponse):
    class Meta:
        swappable = swapper.swappable_setting('rest_surveys', 'SurveyResponse')


class SurveyQuestionResponse(models.Model):
    survey_response = models.ForeignKey(swapper.get_model_name('rest_surveys',
                                                               'SurveyResponse'))
    question = models.ForeignKey('rest_surveys.SurveyQuestion')
    response_option = models.ForeignKey('rest_surveys.SurveyResponseOption',
                                        null=True, blank=True)
    custom_text = models.TextField(null=True, blank=True)
