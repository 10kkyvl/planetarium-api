from django.urls import path, include
from rest_framework.routers import DefaultRouter

from planetarium_api.views import (
    RegisterViewSet,
    ShowsViewSet, AstronomyShowViewSet, ReservationViewSet,
)

router = DefaultRouter()
router.register(r"user/register", RegisterViewSet, basename="user_register")
router.register(r"sessions", ShowsViewSet, basename="sessions")
router.register(r"shows", AstronomyShowViewSet, basename="shows")
router.register(r"reservations", ReservationViewSet, basename="reservations")


urlpatterns = [
    path("", include(router.urls))
]

app_name = "planetarium_api"
