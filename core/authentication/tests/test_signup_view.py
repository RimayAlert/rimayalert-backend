from django.test import TestCase
from django.urls import reverse


class SignupViewTest(TestCase):
    """Tests for the SignupView"""

    def setUp(self):
        self.signup_url = reverse('authentication:signup')

    def test_signup_view_get_context_contains_login_url(self):
        """Test that signup view context contains login_url"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('login_url', response.context)
        self.assertEqual(
            response.context['login_url'],
            reverse('authentication:login')
        )

    def test_signup_view_uses_correct_template(self):
        """Test that signup view uses the correct template"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup/signup.html')

    def test_signup_view_context_contains_title(self):
        """Test that signup view context contains title"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], 'Registro - Code Crafters')

