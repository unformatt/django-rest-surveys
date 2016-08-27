from __future__ import unicode_literals
from django.conf import settings
from django.conf.urls import include, url
from rest_framework import routers
from rest_surveys.views import SurveyViewSet, SurveyResponseViewSet


# API
# With trailing slash appended:
router = routers.SimpleRouter()
router.register(r'survey-responses', SurveyResponseViewSet,
                base_name='survey-response')
router.register(r'surveys', SurveyViewSet)
slashless_router = routers.SimpleRouter(trailing_slash=False)
slashless_router.registry = router.registry[:]

urlpatterns = [
    url(r'^{api_path}'.format(api_path=settings.REST_SURVEYS['API_PATH']),
        include(router.urls)),
    url(r'^{api_path}'.format(api_path=settings.REST_SURVEYS['API_PATH']),
        include(slashless_router.urls)),
]
