from __future__ import unicode_literals
from django.apps import apps
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APITestCase
from rest_surveys.models import (
    SurveyStep,
    SurveyQuestion,
    SurveyResponseOption,
    SurveyQuestionResponseOption,
)
from rest_surveys.serializers import (
    SurveySerializer,
    SurveyResponseSerializer,
)
from .models import Session


Survey = apps.get_model(settings.REST_SURVEYS['SURVEY_MODEL'])
SurveyResponse = apps.get_model(settings.REST_SURVEYS['SURVEY_RESPONSE_MODEL'])

def mock_survey_data(cls):
    # Survey
    title = ('Hi {student_name}, how can we improve things with your mentor'
             ' {mentor_name}?')
    description = ('We\'ll share your feedback with your mentor to help'
                   ' them improve')
    cls.survey = Survey(title=title,
                        description=description)
    cls.survey.save()

    # Survey Step
    cls.survey_step = SurveyStep(survey=cls.survey)
    cls.survey_step.save()

    # Survey Questions
    title = 'Did your mentor give you timely online feedback?'
    description = ('For example, they left comments for you on your'
                   'submissions within 48 hours as expected.')
    cls.survey_question1 = SurveyQuestion(step=cls.survey_step,
                                          title=title,
                                          description=description,
                                          is_required=True,
                                          format=SurveyQuestion.CHOOSE_ONE,
                                          inline_ordering_position=2)
    cls.survey_question1.save()
    title = 'Any additional comments?'
    cls.survey_question2 = SurveyQuestion(step=cls.survey_step,
                                          title=title,
                                          is_required=True,
                                          format=SurveyQuestion.OPEN_ENDED,
                                          inline_ordering_position=1)
    cls.survey_question2.save()

    # Survey Response Options
    cls.survey_response_option1 = SurveyResponseOption(
            text='Strongly Agree')
    cls.survey_response_option1.save()
    cls.survey_response_option2 = SurveyResponseOption(
            text='Somewhat Agree')
    cls.survey_response_option2.save()
    cls.survey_response_option3 = SurveyResponseOption(
            text='Neither Agree Nor Disagree')
    cls.survey_response_option3.save()
    cls.survey_response_option4 = SurveyResponseOption(
            text='Somewhat Disagree')
    cls.survey_response_option4.save()
    cls.survey_response_option5 = SurveyResponseOption(
            text='Strongly Disagree')
    cls.survey_response_option5.save()

    # Survey Question Response Options
    survey_response_options = [
        cls.survey_response_option1,
        cls.survey_response_option2,
        cls.survey_response_option3,
        cls.survey_response_option4,
        cls.survey_response_option5,
    ]
    for i in xrange(len(survey_response_options)):
        survey_response_option = survey_response_options[i]
        survey_question_response_option = SurveyQuestionResponseOption(
            question=cls.survey_question1,
            response_option=survey_response_option,
            inline_ordering_position=i)
        survey_question_response_option.save()

    # Session (SurveyResponse foreign key)
    cls.session = Session()
    cls.session.save()

    # Save the response name.
    cls.response_fk = settings.REST_SURVEYS['SURVEY_RESPONSE_FK_NAME']

    # Survey Response
    field_kwargs = {
        cls.response_fk: cls.session,
        'question': cls.survey_question1,
        'response_option': cls.survey_response_option1,
    }
    cls.survey_response = SurveyResponse(**field_kwargs)
    cls.survey_response.save()


class SurveyResponseTests(APITestCase):

    def setUp(self):
        mock_survey_data(self)

        # Save URLs.
        self.list_url = reverse('survey-response-list')

    def test_create_bulk(self):
        new_response_option = self.survey_response_option2
        custom_text = 'Thank you for being such a great mentor!'
        data = [{
            self.response_fk: self.session.id,
            'question': self.survey_question1.id,
            'response_option': new_response_option.id,
        }, {
            self.response_fk: self.session.id,
            'question': self.survey_question2.id,
            'custom_text': custom_text,
        }]
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # It should delete the old survey response.
        with self.assertRaises(SurveyResponse.DoesNotExist):
            SurveyResponse.objects.get(id=self.survey_response.id)

        # It should create new survey responses.
        survey_response1 = SurveyResponse.objects.get(
                session=self.session,
                question_id=self.survey_response.question,
                response_option=new_response_option)
        survey_response2 = SurveyResponse.objects.get(
                session=self.session,
                question=self.survey_question2,
                custom_text=custom_text)

        # It should return the survey responses.
        survey_responses = [survey_response1, survey_response2]
        serializer = SurveyResponseSerializer(survey_responses, many=True)
        json_survey_responses = JSONRenderer().render(serializer.data)
        self.assertEqual(response.content, json_survey_responses)

    def test_create_bulk_custom_text_for_choose_one(self):
        data = [{
            self.response_fk: self.session.id,
            'question': self.survey_question1.id,
            'custom_text': 'I couldn\'t ask for a better mentor.',
        }]
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bulk_response_option_for_open_ended(self):
        data = [{
            self.response_fk: self.session.id,
            'question': self.survey_question2.id,
            'response_option': self.survey_response_option1.id,
        }]
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create(self):
        data = {
            self.response_fk: self.session.id,
            'question': self.survey_question1.id,
            'response_option': self.survey_response_option2.id,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # It should delete the existing survey response.
        with self.assertRaises(SurveyResponse.DoesNotExist):
            SurveyResponse.objects.get(
                    question=self.survey_response.question,
                    response_option=self.survey_response.response_option)

        # It should create a survey response.
        SurveyResponse.objects.get(question=data['question'],
                                   response_option=data['response_option'])

    def test_create_custom_text_for_choose_one(self):
        data = {
            self.response_fk: self.session.id,
            'question': self.survey_question1.id,
            'custom_text': 'I couldn\'t ask for a better mentor.',
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_response_option_for_open_ended(self):
        data = {
            self.response_fk: self.session.id,
            'question': self.survey_question2.id,
            'response_option': self.survey_response_option1.id,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO: Handle authentication

    def test_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # It should return a list of survey responses.
        serializer = SurveyResponseSerializer([self.survey_response], many=True)
        json_survey_response = JSONRenderer().render(serializer.data)
        self.assertEqual(response.content, json_survey_response)

    def test_list_filter(self):
        # Mock survey responses.
        field_kwargs = {
            self.response_fk: self.session,
            'question': self.survey_question1,
            'response_option': self.survey_response_option1,
        }
        survey_response1 = SurveyResponse(**field_kwargs)
        survey_response1.save()
        field_kwargs = {
            self.response_fk: self.session,
            'question': self.survey_question2,
            'custom_text': 'I couldn\'t ask for a better mentor.',
        }
        survey_response2 = SurveyResponse(**field_kwargs)
        survey_response2.save()

        url = '{list_url}?question={question}'.format(
                list_url=self.list_url,
                question=self.survey_question2.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # It should return a list of survey responses.
        serializer = SurveyResponseSerializer([survey_response2], many=True)
        json_survey_response = JSONRenderer().render(serializer.data)
        self.assertEqual(response.content, json_survey_response)

        # TODO: Limit what you can filter by


class SurveyTests(APITestCase):

    def setUp(self):
        mock_survey_data(self)

        # Save URLs.
        self.detail_url = reverse('survey-detail',
                                  kwargs={'pk': self.survey.id})

    def test_get(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # It should return the survey.
        serializer = SurveySerializer(self.survey)
        json_survey = JSONRenderer().render(serializer.data)
        self.assertEqual(response.content, json_survey)
