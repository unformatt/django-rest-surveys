from __future__ import unicode_literals
from django.apps import apps
from django.conf import settings
from rest_framework import serializers


SurveyResponse = apps.get_model(
        app_label='rest_surveys',
        model_name=settings.REST_SURVEYS['SURVEY_RESPONSE_MODEL'])

class SurveyResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = SurveyResponse

    def validate(self, data):
        """
        Make sure that either `response_option` or `custom_text` are defined.
        """
        if not data.get('response_option') and not data.get('custom_text'):
            error = 'Either `response_option` or `custom_text` must be defined.'
            raise serializers.ValidationError(error) 
        return data
