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
    response_options = serializers.SerializerMethodField()

    class Meta:
        model = SurveyQuestion
        fields = [
            field for field in get_all_model_fields(SurveyQuestion)
            if field not in ('inline_ordering_position', 'step')
        ] + ['response_options']

    def get_response_options(self, obj):
        question_response_options = obj.question_response_options.order_by(
                'inline_ordering_position')
        response_options = [question_response_option.response_option
                            for question_response_option
                            in question_response_options]
        serializer = SurveyResponseOptionSerializer(data=response_options,
                                                    many=True)
        serializer.is_valid()
        return serializer.data


class SurveyStepSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = SurveyStep
        fields = [
            field for field in get_all_model_fields(SurveyStep)
            if field not in ('inline_ordering_position', 'survey')
        ] + ['questions']

    def get_questions(self, obj):
        questions = obj.questions.order_by('inline_ordering_position')
        serializer = SurveyQuestionSerializer(questions, many=True)
        return serializer.data


class SurveySerializer(serializers.ModelSerializer):
    # TODO: All rest_surveys users to define reverse relations for their
    # custom survey models.
    steps = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = get_all_model_fields(Survey) + ['steps']

    def get_steps(self, obj):
        steps = obj.steps.order_by('inline_ordering_position')
        serializer = SurveyStepSerializer(steps, many=True)
        return serializer.data
