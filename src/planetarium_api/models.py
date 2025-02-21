from django.contrib.auth.models import User
from django.db import models


class ShowTheme(models.Model):
    name = models.CharField(max_length=100)


class AstronomyShow(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()
    themes = models.ManyToManyField(
        ShowTheme,
        related_name="shows",
        blank=True
    )


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=120)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(
        AstronomyShow,
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    planetarium_dome = models.ForeignKey(
        PlanetariumDome,
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    show_time = models.DateTimeField()


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(
        ShowSession,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
