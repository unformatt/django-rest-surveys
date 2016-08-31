from __future__ import unicode_literals
from django.apps import apps
from django.conf import settings
from django_filters.utils import get_all_model_fields
from rest_framework import serializers
from rest_surveys.models import (
    SurveyStep,
    SurveyQuestion,
    SurveyResponseOption,
)


Survey = apps.get_model(app_label='rest_surveys',
                        model_name=settings.REST_SURVEYS['SURVEY_MODEL'])
SurveyResponse = apps.get_model(
        app_label='rest_surveys',
        model_name=settings.REST_SURVEYS['SURVEY_RESPONSE_MODEL'])

class SurveyResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = SurveyResponse

    def validate(self, data):
        """
        Make sure that either `response_option` or `custom_text` are defined,
        but not both.
        """
        response_option = data.get('response_option')
        custom_text = data.get('custom_text')
        if not response_option and not custom_text:
            error = 'Either `response_option` or `custom_text` must be defined.'
            raise serializers.ValidationError(error) 
        if response_option and custom_text:
            error = ('Only one of `response_option` and `custom_text` may'
                     'be defined.')
            raise serializers.ValidationError(error) 
        return data


class SurveyResponseOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SurveyResponseOption


class SurveyQuestionSerializer(serializers.ModelSerializer):
    response_options = SurveyResponseOptionSerializer(many=True,
                                                              read_only=True)

    class Meta:
        model = SurveyQuestion
        fields = get_all_model_fields(SurveyQuestion) + ['response_options']


class SurveyStepSerializer(serializers.ModelSerializer):
    questions = SurveyQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = SurveyStep
        fields = get_all_model_fields(SurveyStep) + ['questions']


class SurveySerializer(serializers.ModelSerializer):
    # TODO: All rest_surveys users to define reverse relations for their
    # custom survey models.
    steps = SurveyStepSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = get_all_model_fields(Survey) + ['steps']
