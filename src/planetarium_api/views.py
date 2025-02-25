from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from planetarium_api.models import (
    ShowSession,
    AstronomyShow,
    PlanetariumDome,
    Reservation,
    Ticket
)
from planetarium_api.serializers import (
    RegisterSerializer,
    ShowSessionSerializer,
    ShowSessionListSerializer,
    ShowSessionDetailSerializer,
    AstronomyShowSerializer,
    ShowThemeSerializer,
    PlanetariumDomeSerializer,
    ReservationSerializer,
    TicketSerializer,
    ReservationCreateSerializer
)


class RegisterViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    http_method_names = ["post"]


class ShowThemeViewSet(ModelViewSet):
    queryset = ShowSession.objects.all()
    serializer_class = ShowThemeSerializer


class PlanetariumDomeViewSet(ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class AstronomyShowViewSet(ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer


class ShowsViewSet(ModelViewSet):
    queryset = ShowSession.objects.all().select_related(
        "astronomy_show",
        "planetarium_dome",
    )
    serializer_class = ShowSessionSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        elif self.action == "retrieve":
            return ShowSessionDetailSerializer
        return ShowSessionSerializer


class TicketViewSet(ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]

    def get_serializer_class(self):
        if self.action == "create":
            return ReservationCreateSerializer
        return ReservationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Reservation.objects.all()
        return Reservation.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    @action(detail=False, methods=["post"])
    def create_reservation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            reservation = serializer.save()
            return Response(
                {"reservation_id": reservation.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
