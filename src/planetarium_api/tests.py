from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.utils import timezone
from datetime import datetime, timedelta

from planetarium_api.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
    Ticket
)


class RegisterTests(APITestCase):
    def test_register_user(self):
        url = reverse('planetarium_api:user_register-list')
        data = {'username': 'testuser', 'password': 'securepassword123'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')


class ShowSessionTests(APITestCase):
    def setUp(self):
        self.theme = ShowTheme.objects.create(name="Space Exploration")
        self.show = AstronomyShow.objects.create(
            title="Journey to the Stars",
            description="An amazing journey through our galaxy"
        )
        self.show.themes.add(self.theme)

        self.dome = PlanetariumDome.objects.create(
            name="Main Dome",
            rows=10,
            seats_in_row=15
        )

        tomorrow = timezone.now() + timedelta(days=1)
        self.session = ShowSession.objects.create(
            astronomy_show=self.show,
            planetarium_dome=self.dome,
            show_time=tomorrow
        )

    def test_get_show_sessions_list(self):
        url = reverse('planetarium_api:sessions-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['astronomy_show'], 'Journey to the Stars')

    def test_get_show_session_detail(self):
        url = reverse('planetarium_api:sessions-detail', args=[self.session.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['astronomy_show']['title'], 'Journey to the Stars')
        self.assertEqual(response.data['planetarium_dome']['name'], 'Main Dome')


class AstronomyShowTests(APITestCase):
    def setUp(self):
        self.theme = ShowTheme.objects.create(name="Planets")
        self.show = AstronomyShow.objects.create(
            title="Saturn's Rings",
            description="Explore the beauty of Saturn's rings"
        )
        self.show.themes.add(self.theme)

    def test_get_astronomy_shows(self):
        url = reverse('planetarium_api:shows-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Saturn\'s Rings')

    def test_get_astronomy_show_detail(self):
        url = reverse('planetarium_api:shows-detail', args=[self.show.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Saturn\'s Rings')
        self.assertEqual(len(response.data['themes']), 1)
        self.assertEqual(response.data['themes'][0]['name'], 'Planets')


class ReservationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )

        self.show = AstronomyShow.objects.create(
            title="Mars Exploration",
            description="Discover the red planet"
        )

        self.dome = PlanetariumDome.objects.create(
            name="Secondary Dome",
            rows=8,
            seats_in_row=12
        )

        tomorrow = timezone.now() + timedelta(days=1)
        self.session = ShowSession.objects.create(
            astronomy_show=self.show,
            planetarium_dome=self.dome,
            show_time=tomorrow
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_reservation(self):
        url = reverse('planetarium_api:reservations-list')
        data = {
            'tickets': [
                {
                    'row': 3,
                    'seat': 5,
                    'show_session': self.session.id
                },
                {
                    'row': 3,
                    'seat': 6,
                    'show_session': self.session.id
                }
            ]
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(Ticket.objects.count(), 2)

        reservation = Reservation.objects.first()
        self.assertEqual(reservation.tickets.count(), 2)
        self.assertEqual(reservation.user, self.user)

    def test_duplicate_seat_reservation(self):
        url = reverse('planetarium_api:reservations-list')
        data = {
            'tickets': [
                {
                    'row': 2,
                    'seat': 4,
                    'show_session': self.session.id
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Seat is already taken', str(response.data))

    def test_get_user_reservations(self):
        reservation = Reservation.objects.create(user=self.user)
        Ticket.objects.create(
            reservation=reservation,
            row=1,
            seat=1,
            show_session=self.session
        )

        url = reverse('planetarium_api:reservations-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]['tickets']), 1)


class AuthenticationRequiredTests(APITestCase):
    def setUp(self):
        self.show = AstronomyShow.objects.create(
            title="Solar System Tour",
            description="Visit all planets in our solar system"
        )

        self.dome = PlanetariumDome.objects.create(
            name="Mini Dome",
            rows=5,
            seats_in_row=8
        )

        tomorrow = timezone.now() + timedelta(days=1)
        self.session = ShowSession.objects.create(
            astronomy_show=self.show,
            planetarium_dome=self.dome,
            show_time=tomorrow
        )

    def test_reservation_requires_authentication(self):
        url = reverse('planetarium_api:reservations-list')
        data = {
            'tickets': [
                {
                    'row': 1,
                    'seat': 1,
                    'show_session': self.session.id
                }
            ]
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Reservation.objects.count(), 0)