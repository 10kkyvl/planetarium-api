from django.urls import path, include
from rest_framework.routers import DefaultRouter

from planetarium_api.views import (
    RegisterViewSet,
    ShowsViewSet,
)

router = DefaultRouter()
router.register(r"user/register", RegisterViewSet, basename="user_register")
router.register(r"sessions", ShowsViewSet, basename="sessions")

urlpatterns = [
    path("", include(router.urls))
]

app_name = "planetarium_api"
