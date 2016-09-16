from __future__ import unicode_literals
from django.apps import apps
from django.conf import settings
from django_filters.utils import get_all_model_fields
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_bulk import BulkCreateModelMixin
from rest_surveys.serializers import (
    SurveySerializer,
    SurveyResponseSerializer,
)


Survey = apps.get_model(settings.REST_SURVEYS['SURVEY_MODEL'])
SurveyResponse = apps.get_model(settings.REST_SURVEYS['SURVEY_RESPONSE_MODEL'])

class SurveyResponseViewSet(BulkCreateModelMixin, mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    queryset = SurveyResponse.objects.all()
    serializer_class = SurveyResponseSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = get_all_model_fields(SurveyResponse)
    #permission_classes = settings.REST_SURVEYS.get(
    #       'survey_response_permission_classes')

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            data = kwargs['data']

            if isinstance(data, list):
                kwargs['many'] = True

        return super(SurveyResponseViewSet, self).get_serializer(*args, **kwargs)


class SurveyViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    authentication_classes = (SessionAuthentication,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = get_all_model_fields(SurveyResponse)
    permission_classes = (IsAuthenticated,)
