from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueTogetherValidator

from planetarium_api.models import (
    ShowSession,
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    Ticket,
    Reservation,
)


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ("id", "name")


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seats_in_row")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat", "show_session")


class TicketCreateSerializer(serializers.ModelSerializer):
    show_session = serializers.PrimaryKeyRelatedField(
        queryset=ShowSession.objects.all()
    )

    class Meta:
        model = Ticket
        exclude = ("reservation",)
        validators = (
            UniqueTogetherValidator(
                queryset=Ticket.objects.all(),
                fields=("row", "seat", "show_session"),
                message="Seat is already taken."
            ),
        )


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True)

    class Meta:
        model = Reservation
        fields = "__all__"


class ReservationCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(many=True)

    class Meta:
        model = Reservation
        fields = ("tickets",)

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")

        user = self.context["request"].user

        if not user.is_authenticated:
            raise serializers.ValidationError(
                "Must be authenticated to create a reservation."
            )

        reservation = Reservation.objects.create(user=user)

        Ticket.objects.bulk_create(
            [
                Ticket(
                    reservation=reservation,
                    **ticket_data
                ) for ticket_data in tickets_data
            ]
        )

        return reservation


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = "__all__"


class ShowSessionListSerializer(ShowSessionSerializer):
    astronomy_show = serializers.SlugRelatedField(
        slug_field="title",
        read_only=True
    )
    planetarium_dome = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True
    )


class AstronomyShowSerializer(serializers.ModelSerializer):
    themes = ShowThemeSerializer(many=True, read_only=True)
    sessions = ShowSessionSerializer(many=True, read_only=True)

    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "themes", "sessions")


class ShowSessionDetailSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowSerializer(read_only=True)
    planetarium_dome = PlanetariumDomeSerializer(read_only=True)
