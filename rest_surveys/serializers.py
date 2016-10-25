from __future__ import unicode_literals
from django.conf import settings
from rest_framework import serializers
from rest_surveys.models import (
    SurveyStep,
    SurveyQuestion,
    SurveyResponseOption,
)
from rest_surveys.utils import get_field_names

import swapper


Survey = swapper.load_model('rest_surveys', 'Survey')
SurveyResponse = swapper.load_model('rest_surveys', 'SurveyResponse')

class SurveyResponseListSerializer(serializers.ListSerializer):

    def create(self, validated_data):
        """
        Delete any old survey responses to "choose one" questions, then create
        the survey responses.
        """
        response_fk = settings.REST_SURVEYS['SURVEY_RESPONSE_FK_NAME']

        for response in validated_data:
            one_response_formats = [
                SurveyQuestion.CHOOSE_ONE,
                SurveyQuestion.OPEN_ENDED,
            ]
            if response['question'].format not in one_response_formats:
                continue
            filter_kwargs = {
                'question': response['question'],
                response_fk: response[response_fk],
            }
            SurveyResponse.objects.filter(**filter_kwargs).delete()

        # Create new responses.
        responses = []
        for response in validated_data:
            field_kwargs = {
                'question': response['question'],
                response_fk: response[response_fk],
            }
            response_option = response.get('response_option')
            custom_text = response.get('custom_text')
            if response_option:
                field_kwargs['response_option'] = response_option
            elif custom_text:
                field_kwargs['custom_text'] = custom_text
            new_response = SurveyResponse(**field_kwargs)
            new_response.save()
            responses.append(new_response)
        return responses


class SurveyResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = SurveyResponse
        list_serializer_class = SurveyResponseListSerializer

    def validate(self, data):
        """
        Make sure that "choose one" questions have response options, and
        "open ended" questions have custom text.
        """
        response_option = data.get('response_option')
        custom_text = data.get('custom_text')
        question = data.get('question')

        # Make sure "choose one" questions don't have custom text.
        if question.format == question.CHOOSE_ONE and custom_text:
            error = '"Choose one" questions can\'t have `custom_text` set'
            raise serializers.ValidationError(error)

        # Make sure "open ended" questions don't have a response option.
        if question.format == question.OPEN_ENDED and response_option:
            error = '"Open ended" questions can\'t have `response_option` set.'
            raise serializers.ValidationError(error)

        return data

    def create(self, validated_data):
        """
        If this is a "choose one" question, delete any old survey responses
        to the question.
        """
        response = validated_data
        if response['question'].format == SurveyQuestion.CHOOSE_ONE:
            response_fk = settings.REST_SURVEYS['SURVEY_RESPONSE_FK_NAME']
            filter_kwargs = {
                'question': response['question'],
                response_fk: response[response_fk],
            }
            SurveyResponse.objects.filter(**filter_kwargs).delete()

        return super(SurveyResponseSerializer, self).create(validated_data)


class SurveyResponseOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SurveyResponseOption


class SurveyQuestionSerializer(serializers.ModelSerializer):
    response_options = serializers.SerializerMethodField()

    class Meta:
        model = SurveyQuestion
        fields = [
            field for field in get_field_names(SurveyQuestion)
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
            field for field in get_field_names(SurveyStep)
            if field not in ('inline_ordering_position', 'survey')
        ] + ['questions']

    def get_questions(self, obj):
        questions = obj.questions.order_by('inline_ordering_position')
        serializer = SurveyQuestionSerializer(questions, many=True)
        return serializer.data


class SurveySerializer(serializers.ModelSerializer):
    steps = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = get_field_names(Survey) + ['steps']

    def get_steps(self, obj):
        steps = obj.steps.order_by('inline_ordering_position')
        serializer = SurveyStepSerializer(steps, many=True)
        return serializer.data
