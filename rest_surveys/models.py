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

    def __str__(self):
        return '{0}'.format(self.title)


class Survey(AbstractSurvey):
    class Meta:
        swappable = swapper.swappable_setting('rest_surveys', 'Survey')


class SurveyStep(Orderable):
    survey = models.ForeignKey(swapper.get_model_name('rest_surveys', 'Survey'),
                               related_name='steps', on_delete=models.CASCADE)
    title = models.TextField(blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return '{0} ({1}): {2}'.format(
            self.survey, self.inline_ordering_position, self.title)


class SurveyQuestion(Orderable):
    step = models.ForeignKey('rest_surveys.SurveyStep',
                             related_name='questions', on_delete=models.CASCADE)
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
        choices=FORMAT_CHOICES
    )
    response_options = models.ManyToManyField(
        'rest_surveys.SurveyResponseOption',
        blank=True,
        through='rest_surveys.SurveyQuestionResponseOption'
    )


class SurveyResponseOption(models.Model):
    text = models.TextField()

    def __str__(self):
        return '{0}'.format(self.text)


class SurveyQuestionResponseOption(Orderable):
    question = models.ForeignKey('rest_surveys.SurveyQuestion',
                                 related_name='question_response_options', on_delete=models.CASCADE)
    response_option = models.ForeignKey('rest_surveys.SurveyResponseOption',
                                        related_name='question_response_options', on_delete=models.CASCADE)


class AbstractSurveyResponse(models.Model):
    survey = models.ForeignKey(swapper.get_model_name('rest_surveys', 'Survey'), on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class SurveyResponse(AbstractSurveyResponse):
    class Meta:
        swappable = swapper.swappable_setting('rest_surveys', 'SurveyResponse')


class SurveyQuestionResponse(models.Model):
    survey_response = models.ForeignKey(swapper.get_model_name(
        'rest_surveys', 'SurveyResponse'
    ), related_name='question_responses', on_delete=models.CASCADE)
    question = models.ForeignKey('rest_surveys.SurveyQuestion', on_delete=models.CASCADE)
    response_option = models.ForeignKey('rest_surveys.SurveyResponseOption',
                                        null=True, blank=True, on_delete=models.CASCADE)
    custom_text = models.TextField(null=True, blank=True)
