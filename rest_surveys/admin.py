from __future__ import unicode_literals

from django.contrib import admin

import swapper
from inline_ordering.admin import OrderableStackedInline

from rest_surveys.models import SurveyStep, SurveyQuestion,\
    SurveyQuestionResponseOption, SurveyResponseOption
from rest_surveys.utils import admin_edit_link

Survey = swapper.load_model('rest_surveys', 'Survey')
SurveyResponse = swapper.load_model('rest_surveys', 'SurveyResponse')


class SurveyStepInline(OrderableStackedInline):
    model = SurveyStep
    extra = 0


class SurveyAdmin(admin.ModelAdmin):
    model = Survey
    inlines = [SurveyStepInline]


class SurveyQuestionInline(OrderableStackedInline):
    model = SurveyQuestion
    extra = 0


class SurveyStepAdmin(admin.ModelAdmin):
    model = SurveyStep
    inlines = [SurveyQuestionInline]
    list_filter = ['survey']
    list_display = ['id', 'title', 'position', 'survey_link']

    def position(self, survey_step):
        return survey_step.inline_ordering_position

    def survey_link(self, survey_step):
        return admin_edit_link(survey_step.survey)
    survey_link.allow_tags = True
    survey_link.short_description = 'Survey'


class SurveyQuestionResponseOptionInline(OrderableStackedInline):
    model = SurveyQuestionResponseOption
    extra = 0


class SurveyQuestionAdmin(admin.ModelAdmin):
    model = SurveyQuestion
    inlines = [SurveyQuestionResponseOptionInline]
    exclude = ['response_options']
    list_display = ['title', 'step_position', 'survey']
    list_filter = ['step__survey']
    ordering = ['step__inline_ordering_position', 'inline_ordering_position']

    def step_position(self, question):
        return question.step.inline_ordering_position
    step_position.admin_order_field = 'step__inline_ordering_position'

    def survey(self, question):
        return admin_edit_link(question.step.survey)
    survey.admin_order_field = 'step__survey__title'
    survey.allow_tags = True


class SurveyResponseOptionAdmin(admin.ModelAdmin):
    model = SurveyResponseOption


admin.site.register(Survey, SurveyAdmin)
admin.site.register(SurveyStep, SurveyStepAdmin)
admin.site.register(SurveyQuestion, SurveyQuestionAdmin)
admin.site.register(SurveyResponseOption, SurveyResponseOptionAdmin)
