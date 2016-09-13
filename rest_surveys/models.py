from __future__ import unicode_literals
from django.db import models
from django.conf import settings
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
    pass


SURVEY_MODEL = getattr(settings, 'SURVEY_MODEL', Survey)

class SurveyStep(Orderable):
    survey = models.ForeignKey(SURVEY_MODEL)
    title = models.TextField()
    description = models.TextField(null=True, blank=True)

    class Meta:
        default_related_name = 'steps'


class SurveyQuestion(Orderable):
    step = models.ForeignKey('SurveyStep')
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    is_required = models.BooleanField()
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
            'SurveyResponseOption',
            blank=True,
            through='SurveyQuestionResponseOption')

    class Meta:
        default_related_name = 'questions'


class SurveyResponseOption(models.Model):
    text = models.TextField()

    class Meta:
        default_related_name = 'response_options'


class SurveyQuestionResponseOption(Orderable):
    question = models.ForeignKey('SurveyQuestion')
    response_option = models.ForeignKey('SurveyResponseOption')

    class Meta:
        default_related_name = 'question_response_options'


class AbstractSurveyResponse(models.Model):
    question = models.ForeignKey('SurveyQuestion')
    response_option = models.ForeignKey('SurveyResponseOption', null=True,
                                        blank=True)
    custom_text = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class SurveyResponse(AbstractSurveyResponse):
    pass
