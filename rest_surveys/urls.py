from django.conf import settings
from django.urls import include, re_path
from rest_framework_bulk.routes import BulkRouter
from rest_surveys.views import (
    SurveyViewSet,
    SurveyResponseViewSet,
)


# API
# With trailing slash appended:
router = BulkRouter()
router.register(r'surveys', SurveyViewSet, base_name='survey')
router.register(r'survey-responses', SurveyResponseViewSet,
                base_name='survey-response')
slashless_router = BulkRouter(trailing_slash=False)
slashless_router.registry = router.registry[:]

urlpatterns = [
    re_path(r'^{api_path}'.format(
        api_path=getattr(settings, 'REST_SURVEYS_API_PATH', 'api/')),
        include(router.urls)),
    re_path(r'^{api_path}'.format(
        api_path=getattr(settings, 'REST_SURVEYS_API_PATH', 'api/')),
        include(slashless_router.urls)),
]
