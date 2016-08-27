from __future__ import unicode_literals
from django.apps import apps
from django.conf import settings
from django.core.urlresolvers import reverse
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


Survey = apps.get_model(app_label='rest_surveys',
                        model_name=settings.REST_SURVEYS['SURVEY_MODEL'])
SurveyResponse = apps.get_model(
        app_label='rest_surveys',
        model_name=settings.REST_SURVEYS['SURVEY_RESPONSE_MODEL'])

class SurveyResponseTests(APITestCase):

    def setUp(self):
        # Mock survey data.

        # Survey
        title = ('Hi {student_name}, how can we improve things with your mentor'
                 ' {mentor_name}?')
        description = ('We\'ll share your feedback with your mentor to help'
                       ' them improve')
        self.survey = Survey(title=title,
                             description=description)
        self.survey.save()

        # Survey Step
        self.survey_step = SurveyStep(survey=self.survey)
        self.survey_step.save()

        # Survey Questions
        title = 'Did your mentor give you timely online feedback?'
        description = ('For example, they left comments for you on your'
                       'submissions within 48 hours as expected.')
        self.survey_question1 = SurveyQuestion(step=self.survey_step,
                                               title=title,
                                               description=description,
                                               is_required=True,
                                               format=SurveyQuestion.CHOOSE_ONE)
        self.survey_question1.save()
        title = 'Any additional comments?'
        self.survey_question2 = SurveyQuestion(step=self.survey_step,
                                               title=title,
                                               is_required=True,
                                               format=SurveyQuestion.OPEN_ENDED)
        self.survey_question2.save()

        # Survey Response Options
        self.survey_response_option1 = SurveyResponseOption(
                text='Strongly Agree')
        self.survey_response_option1.save()
        self.survey_response_option2 = SurveyResponseOption(
                text='Somewhat Agree')
        self.survey_response_option2.save()
        self.survey_response_option3 = SurveyResponseOption(
                text='Neither Agree Nor Disagree')
        self.survey_response_option3.save()
        self.survey_response_option4 = SurveyResponseOption(
                text='Somewhat Disagree')
        self.survey_response_option4.save()
        self.survey_response_option5 = SurveyResponseOption(
                text='Strongly Disagree')
        self.survey_response_option5.save()

        # Survey Question Response Options
        survey_response_options = [
            self.survey_response_option1,
            self.survey_response_option2,
            self.survey_response_option3,
            self.survey_response_option4,
            self.survey_response_option5,
        ]
        for i in xrange(len(survey_response_options)):
            survey_response_option = survey_response_options[i]
            survey_question_response_option = SurveyQuestionResponseOption(
                question=self.survey_question1,
                response_option=survey_response_option,
                inline_ordering_position=i)
            survey_question_response_option.save()

        # Save URLs.
        self.list_url = reverse('survey-response-list')

    def test_create_choose_one(self):
        data = {
            'question': self.survey_question1.id,
            'response_option': self.survey_response_option1.id,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # It should create a survey response.
        SurveyResponse.objects.get(question=data['question'],
                                   response_option=data['response_option'])

    def test_create_open_ended(self):
        data = {
            'question': self.survey_question2.id,
            'custom_text': 'I couldn\'t ask for a better mentor.',
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # It should create a survey response.
        SurveyResponse.objects.get(question=data['question'],
                                   custom_text=data['custom_text'])

    def test_create_no_response(self):
        data = {
            'question': self.survey_question2.id,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_response_option_and_custom_text(self):
        data = {
            'question': self.survey_question1.id,
            'response_option': self.survey_response_option1.id,
            'custom_text': 'I couldn\'t ask for a better mentor.',
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO: Handle authentication

    def test_list(self):
        # Mock a survey response.
        survey_response = SurveyResponse(
                question=self.survey_question1,
                response_option=self.survey_response_option1)
        survey_response.save()

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # It should return a list of survey responses.
        serializer = SurveyResponseSerializer([survey_response], many=True)
        json_survey_response = JSONRenderer().render(serializer.data)
        self.assertEqual(response.content, json_survey_response)

    def test_list_filter(self):
        # Mock survey responses.
        survey_response1 = SurveyResponse(
                question=self.survey_question1,
                response_option=self.survey_response_option1)
        survey_response1.save()
        survey_response2 = SurveyResponse(
                question=self.survey_question2,
                custom_text='I couldn\'t ask for a better mentor.')
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

    def test_update(self):
        # Mock a survey response.
        survey_response = SurveyResponse(
                question=self.survey_question2,
                custom_text='I couldn\'t ask for a better mentor.')
        survey_response.save()

        data = {
            'question': survey_response.question_id,
            'custom_text': 'I really couldn\'t ask for a better mentor.',
        }
        url = '{list_url}/{id}'.format(list_url=self.list_url,
                                       id=survey_response.id)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # It should update the survey response.
        SurveyResponse.objects.get(id=survey_response.id,
                                   custom_text=data['custom_text'])


class SurveyTests(APITestCase):

    def setUp(self):
        # Mock survey data.

        # Survey
        title = ('Hi {student_name}, how can we improve things with your mentor'
                 ' {mentor_name}?')
        description = ('We\'ll share your feedback with your mentor to help'
                       ' them improve')
        self.survey = Survey(title=title,
                             description=description)
        self.survey.save()

        # Survey Step
        self.survey_step = SurveyStep(survey=self.survey)
        self.survey_step.save()

        # Survey Questions
        title = 'Did your mentor give you timely online feedback?'
        description = ('For example, they left comments for you on your'
                       'submissions within 48 hours as expected.')
        self.survey_question1 = SurveyQuestion(step=self.survey_step,
                                               title=title,
                                               description=description,
                                               is_required=True,
                                               format=SurveyQuestion.CHOOSE_ONE)
        self.survey_question1.save()
        title = 'Any additional comments?'
        self.survey_question2 = SurveyQuestion(step=self.survey_step,
                                               title=title,
                                               is_required=True,
                                               format=SurveyQuestion.OPEN_ENDED)
        self.survey_question2.save()

        # Survey Response Options
        self.survey_response_option1 = SurveyResponseOption(
                text='Strongly Agree')
        self.survey_response_option1.save()
        self.survey_response_option2 = SurveyResponseOption(
                text='Somewhat Agree')
        self.survey_response_option2.save()
        self.survey_response_option3 = SurveyResponseOption(
                text='Neither Agree Nor Disagree')
        self.survey_response_option3.save()
        self.survey_response_option4 = SurveyResponseOption(
                text='Somewhat Disagree')
        self.survey_response_option4.save()
        self.survey_response_option5 = SurveyResponseOption(
                text='Strongly Disagree')
        self.survey_response_option5.save()

        # Survey Question Response Options
        survey_response_options = [
            self.survey_response_option1,
            self.survey_response_option2,
            self.survey_response_option3,
            self.survey_response_option4,
            self.survey_response_option5,
        ]
        for i in xrange(len(survey_response_options)):
            survey_response_option = survey_response_options[i]
            survey_question_response_option = SurveyQuestionResponseOption(
                question=self.survey_question1,
                response_option=survey_response_option,
                inline_ordering_position=i)
            survey_question_response_option.save()

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
