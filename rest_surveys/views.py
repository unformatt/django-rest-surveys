from __future__ import unicode_literals
from django.apps import apps
from django.conf import settings
from django_filters.utils import get_all_model_fields
from rest_framework import filters, mixins, viewsets
from rest_surveys.serializers import SurveyResponseSerializer


SurveyResponse = apps.get_model(
        app_label='rest_surveys',
        model_name=settings.REST_SURVEYS['SURVEY_RESPONSE_MODEL'])

class SurveyResponseViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    queryset = SurveyResponse.objects.all()
    serializer_class = SurveyResponseSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = get_all_model_fields(SurveyResponse)
