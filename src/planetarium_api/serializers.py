from rest_framework import serializers
from django.contrib.auth.models import User

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


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"


class AstronomyShowSerializer(serializers.ModelSerializer):
    themes = ShowThemeSerializer(many=True, read_only=True)

    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "themes")


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


class ShowSessionDetailSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowSerializer(read_only=True)
    planetarium_dome = PlanetariumDomeSerializer(read_only=True)
