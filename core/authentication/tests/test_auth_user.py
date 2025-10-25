import secrets

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.authentication.api.auth.features.user import AuthApiUser
from core.authentication.models import User


class TestAuthApiUser(TestCase):

    def setUp(self):
        self.client = APIClient()
        # self.login_url = reverse('authentication:api_login')
        self.login_url = '/api/auth/login'
        pwd = secrets.token_urlsafe(32)
        self.user_data = {
            "dni": "1723456789",
            "first_name": "Juan",
            "last_name": "Vásquez",
            "email": "juan@example.com",
            "username": "juan_victores",
            "password": pwd,
        }


    def test_login_creates_user_and_returns_token(self):
        response = self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(dni=self.user_data['dni']).exists())
        self.assertIn('token', response.data)

    def test_login_token_is_unique_per_user(self):
        result1 = AuthApiUser(None).login(self.user_data)
        token1 = result1['token']

        result2 = AuthApiUser(None).login(self.user_data)
        token2 = result2['token']

        self.assertEqual(token1, token2)

    def test_user_get_full_name_returns_uppercase(self):
        """Test that get_full_name returns uppercase full name"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Juan',
            last_name='Pérez'
        )
        expected_full_name = 'JUAN PÉREZ'
        self.assertEqual(user.get_full_name(), expected_full_name)

    def test_user_str_method_returns_full_name(self):
        """Test that __str__ method returns the full name"""
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
            first_name='María',
            last_name='González'
        )
        self.assertEqual(str(user), user.get_full_name())
        self.assertEqual(str(user), 'MARÍA GONZÁLEZ')

