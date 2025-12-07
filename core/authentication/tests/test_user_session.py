import secrets

from django.contrib.auth.models import Group
from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

from core.authentication.models import User


class UserSessionMethodsTest(TestCase):
    """Test suite for User session-related methods"""

    def setUp(self):
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=secrets.token_urlsafe(32),
            first_name='Test',
            last_name='User',
            dni='1234567890'
        )
        self.group1 = Group.objects.create(name='Group1')
        self.group2 = Group.objects.create(name='Group2')

    def _add_session_to_request(self, request):
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def test_get_group_session_returns_group_when_exists(self):
        request = self.factory.get('/')
        request = self._add_session_to_request(request)
        request.session['group_id'] = self.group1.id

        result = self.user.get_group_session(request)

        self.assertEqual(result, self.group1)

    def test_get_group_session_returns_none_when_not_exists(self):
        request = self.factory.get('/')
        request = self._add_session_to_request(request)

        result = self.user.get_group_session(request)

        self.assertIsNone(result)

    def test_set_group_session_creates_session_when_user_has_groups(self):
        self.user.groups.add(self.group1, self.group2)

        request = self.factory.get('/')
        request = self._add_session_to_request(request)

        self.assertNotIn('group', request.session)

        self.user.set_group_session(request)

        self.assertIn('group_id', request.session)
        self.assertEqual(request.session['group_id'], self.group1.id)

    def test_set_group_session_does_not_create_when_user_has_no_groups(self):
        request = self.factory.get('/')
        request = self._add_session_to_request(request)
        self.user.set_group_session(request)
        self.assertNotIn('group', request.session)

    def test_set_group_session_does_not_override_existing_session(self):
        self.user.groups.add(self.group1, self.group2)

        request = self.factory.get('/')
        request = self._add_session_to_request(request)
        request.session['group_id'] = self.group2.id

        self.user.set_group_session(request)
        self.assertEqual(request.session['group_id'], self.group2.id)

    def test_set_group_session_selects_first_group_by_id(self):
        self.user.groups.add(self.group2, self.group1)

        request = self.factory.get('/')
        request = self._add_session_to_request(request)

        self.user.set_group_session(request)
        expected_group = self.user.groups.all().order_by('id').first()
        self.assertEqual(request.session['group_id'], expected_group.id)

