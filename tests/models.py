from django.db import models
from rest_surveys.models import AbstractSurveyResponse


class Session(models.Model):
    has_feedback = models.BooleanField(default=False)


class SessionSurveyResponse(AbstractSurveyResponse):
    session = models.ForeignKey('tests.Session')


