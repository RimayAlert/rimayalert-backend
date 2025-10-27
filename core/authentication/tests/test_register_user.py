import secrets

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.authentication.models import User


class TestRegisterApiUser(TestCase):

    def setUp(self):
        self.client = APIClient()
        # self.login_url = reverse('authentication:api_login')
        self.url  = '/api/register/user'
        self.pwd = secrets.token_urlsafe(32)
        self.user_data = {
            "dni": "1723456789",
            "firstName": "jayden",
            "lastName": "zambrano",
            "email": "jayden@example.com",
            "username": "jayden_zambrano",
            "password": self.pwd,
            "displayName": "jayden Z."
        }

    def test_register_creates_user_and_returns_201(self):
        response = self.client.post(self.url, self.user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(dni=self.user_data['dni']).exists())
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'User registered successfully')

    def test_register_duplicate_user_returns_400(self):
        self.client.post(self.url, self.user_data, format='json')
        response = self.client.post(self.url, self.user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)

    def test_user_get_full_name_returns_uppercase(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=secrets.token_urlsafe(32),
            first_name='josue',
            last_name='zq'
        )
        expected_full_name = 'JOSUE ZQ'
        self.assertEqual(user.get_full_name(), expected_full_name)

    def test_user_str_method_returns_full_name(self):
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password=secrets.token_urlsafe(32),
            first_name='María',
            last_name='González'
        )
        self.assertEqual(str(user), user.get_full_name())
