from __future__ import unicode_literals
from rest_framework import serializers
from rest_surveys.models import (
    SurveyStep,
    SurveyQuestion,
    SurveyResponseOption,
    SurveyQuestionResponse
)
from rest_surveys.utils import get_field_names

import swapper


Survey = swapper.load_model('rest_surveys', 'Survey')
SurveyResponse = swapper.load_model('rest_surveys', 'SurveyResponse')

class SurveyQuestionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestionResponse
        exclude = ['survey_response']

    def validate(self, data):
        response_option = data.get('response_option', None)
        custom_text = data.get('custom_text', None)
        question = data.get('question', None)

        # Validate "choose one"
        if question.format == question.CHOOSE_ONE:
            if custom_text:
                error = '"Choose one" questions can\'t have `custom_text` set'
                raise serializers.ValidationError(error)

            if not response_option:
                error = '"Choose one" questions must have `response_option` set'
                raise serializers.ValidationError(error)

        # Make sure "open ended" questions don't have a response option.
        if question.format == question.OPEN_ENDED and response_option:
            error = '"Open ended" questions can\'t have `response_option` set.'
            raise serializers.ValidationError(error)

        # If there's a response option, make sure it's for this question
        if response_option and response_option not in \
                                    question.response_options.all():
            error = 'Invalid response_option {0} for question {1}'\
                .format(response_option.pk, question.pk)
            raise serializers.ValidationError(error)

        return data


class SurveyResponseSerializer(serializers.ModelSerializer):
    question_responses = SurveyQuestionResponseSerializer(many=True)

    class Meta:
        fields = '__all__'
        model = SurveyResponse

    def validate_question_responses(self, value):
        question_responses = value

        # Make sure there is at least 1 question response
        if not question_responses:
            error = '`question_responses` cannot be empty'
            raise serializers.ValidationError(error)

        # Make sure there is at most 1 response for each "choose one" question
        one_response_used = set()
        one_response_formats = [
            SurveyQuestion.CHOOSE_ONE,
            SurveyQuestion.OPEN_ENDED,
        ]

        for question_response in question_responses:
            question = question_response['question']

            if question.format not in one_response_formats:
                continue

            if question.pk in one_response_used:
                error = '"Choose one" or "Open ended" questions can only have 1 response'
                raise serializers.ValidationError(error)
            else:
                one_response_used.add(question.pk)

        return value

    def validate(self, data):
        """
        Make sure all responses are for quesitons for the correct survey
        """
        survey = data.get('survey', None)
        question_responses = data.get('question_responses', None)

        for question_response in question_responses:
            question = question_response['question']
            if question.step.survey != survey:
                error = 'question {0} is not in survey {1}'\
                    .format(question.pk, survey.pk)
                raise serializers.ValidationError(error)

        return data

    def create(self, validated_data):
        """
        Create a survey response along with nested question responses
        """
        question_responses = validated_data.pop('question_responses')
        survey_response = super(SurveyResponseSerializer, self).create(validated_data)

        for question_response in question_responses:
            SurveyQuestionResponse.objects.create(survey_response=survey_response,
                                                  **question_response)

        return survey_response

    def update(self, instance, validated_data):
        """
        Add or update question responses
        """
        question_responses = validated_data.get('question_responses')

        # Delete all existing question responses for any questions
        # that correspond to the responses we are updating with.
        updated_questions = {r['question'] for r in question_responses}
        instance.question_responses.filter(question__in=
                                           updated_questions).delete()

        for question_response in question_responses:
            SurveyQuestionResponse.objects.create(survey_response=instance,
                                                  **question_response)

        return instance

class SurveyResponseOptionSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
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
