from __future__ import unicode_literals
from django.conf import settings
from rest_framework import filters, mixins, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_bulk import BulkCreateModelMixin
from rest_surveys.serializers import (
    SurveySerializer,
    SurveyResponseSerializer,
)
from rest_surveys.utils import get_field_names

import swapper


Survey = swapper.load_model('rest_surveys', 'Survey')
SurveyResponse = swapper.load_model('rest_surveys', 'SurveyResponse')

class SurveyResponseViewSet(BulkCreateModelMixin, mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    queryset = SurveyResponse.objects.all()
    serializer_class = SurveyResponseSerializer
    authentication_classes = settings.REST_SURVEYS.get(
           'SURVEY_RESPONSE_AUTHENTICATION_CLASSES', (SessionAuthentication,))
    permission_classes = settings.REST_SURVEYS.get(
           'SURVEY_RESPONSE_PERMISSION_CLASSES', (IsAuthenticated,))
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = settings.REST_SURVEYS.get(
           'SURVEY_RESPONSE_FILTER_FIELDS',
           get_field_names(SurveyResponse))

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            data = kwargs['data']

            if isinstance(data, list):
                kwargs['many'] = True

        return super(SurveyResponseViewSet, self).get_serializer(*args, **kwargs)


class SurveyViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    authentication_classes = settings.REST_SURVEYS.get(
           'SURVEY_AUTHENTICATION_CLASSES', (SessionAuthentication,))
    permission_classes = settings.REST_SURVEYS.get(
           'SURVEY_PERMISSION_CLASSES', (IsAuthenticated,))
