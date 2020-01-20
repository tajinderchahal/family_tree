from django.urls import path
from rest_framework import routers

from .views import PeopleViewSet

router = routers.SimpleRouter()
router.register(r'people', PeopleViewSet)

urlpatterns = router.urls
