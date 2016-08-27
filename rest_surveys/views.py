from __future__ import unicode_literals
from django.apps import apps
from django.conf import settings
from rest_framework import mixins, viewsets
from rest_surveys.serializers import SurveyResponseSerializer


SurveyResponse = apps.get_model(
        app_label='rest_surveys',
        model_name=settings.REST_SURVEYS['SURVEY_RESPONSE_MODEL'])

class SurveyResponseViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    queryset = SurveyResponse.objects.all()
    serializer_class = SurveyResponseSerializer
