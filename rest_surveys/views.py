from __future__ import unicode_literals
from django.conf import settings
from rest_framework import filters, mixins, viewsets
from rest_surveys.serializers import SurveySerializer
from rest_surveys.utils import get_field_names, to_class

import swapper


Survey = swapper.load_model('rest_surveys', 'Survey')
SurveyResponse = swapper.load_model('rest_surveys', 'SurveyResponse')

class SurveyResponseViewSet(mixins.RetrieveModelMixin,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            viewsets.GenericViewSet):
    queryset = SurveyResponse.objects.all()
    serializer_class = to_class(
        getattr(
            settings,
            'REST_SURVEYS_SURVEYRESPONSE_SERIALIZER',
            'rest_surveys.serializers.SurveyResponseSerializer'
        )
    )
    authentication_classes = [to_class(authentication_class) for authentication_class in getattr(
        settings,
        'REST_SURVEYS_SURVEYRESPONSE_AUTHENTICATION_CLASSES',
        ['rest_framework.authentication.SessionAuthentication']
    )]
    permission_classes = [to_class(permission_class) for permission_class in getattr(
        settings,
        'REST_SURVEYS_SURVEYRESPONSE_PERMISSION_CLASSES',
        ['rest_framework.permissions.IsAuthenticated']
    )]
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = getattr(settings,
                            'REST_SURVEYS_SURVEYRESPONSE_FILTER_FIELDS',
                            get_field_names(SurveyResponse))


class SurveyViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    authentication_classes = [to_class(authentication_class) for authentication_class in getattr(
        settings,
        'REST_SURVEYS_SURVEY_AUTHENTICATION_CLASSES',
        ['rest_framework.authentication.SessionAuthentication']
    )]
    permission_classes = [to_class(permission_class) for permission_class in getattr(
        settings,
        'REST_SURVEYS_SURVEY_PERMISSION_CLASSES',
        ['rest_framework.permissions.IsAuthenticated']
    )]
