"""
Tests for User session methods (get_group_session, set_group_session)
"""
import secrets

from django.contrib.auth.models import Group
from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

from core.authentication.models import User


class UserSessionMethodsTest(TestCase):
    """Test suite for User session-related methods"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

        # Create test user with secure password
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=secrets.token_urlsafe(32),
            first_name='Test',
            last_name='User',
            dni='1234567890'
        )

        # Create test groups
        self.group1 = Group.objects.create(name='Group1')
        self.group2 = Group.objects.create(name='Group2')

    def _add_session_to_request(self, request):
        """Helper method to add session to request"""
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def test_get_group_session_returns_group_when_exists(self):
        """Test get_group_session returns group when it exists in session"""
        request = self.factory.get('/')
        request = self._add_session_to_request(request)
        request.session['group'] = self.group1

        result = self.user.get_group_session(request)

        self.assertEqual(result, self.group1)

    def test_get_group_session_returns_none_when_not_exists(self):
        """Test get_group_session returns None when group doesn't exist in session"""
        request = self.factory.get('/')
        request = self._add_session_to_request(request)

        result = self.user.get_group_session(request)

        self.assertIsNone(result)

    def test_set_group_session_creates_session_when_user_has_groups(self):
        """Test set_group_session creates session when user has groups"""
        # Add groups to user
        self.user.groups.add(self.group1, self.group2)

        request = self.factory.get('/')
        request = self._add_session_to_request(request)

        # Ensure group is not in session initially
        self.assertNotIn('group', request.session)

        # Call set_group_session
        self.user.set_group_session(request)

        # Verify group was added to session
        self.assertIn('group', request.session)
        # Should be the first group (ordered by id)
        self.assertEqual(request.session['group'], self.group1)

    def test_set_group_session_does_not_create_when_user_has_no_groups(self):
        """Test set_group_session doesn't create session when user has no groups"""
        request = self.factory.get('/')
        request = self._add_session_to_request(request)

        # Call set_group_session
        self.user.set_group_session(request)

        # Verify group was NOT added to session
        self.assertNotIn('group', request.session)

    def test_set_group_session_does_not_override_existing_session(self):
        """Test set_group_session doesn't override existing group in session"""
        self.user.groups.add(self.group1, self.group2)

        request = self.factory.get('/')
        request = self._add_session_to_request(request)
        request.session['group'] = self.group2

        # Call set_group_session
        self.user.set_group_session(request)

        # Verify group was NOT changed
        self.assertEqual(request.session['group'], self.group2)

    def test_set_group_session_selects_first_group_by_id(self):
        """Test set_group_session selects first group ordered by id"""
        # Add groups in reverse order
        self.user.groups.add(self.group2, self.group1)

        request = self.factory.get('/')
        request = self._add_session_to_request(request)

        self.user.set_group_session(request)

        # Should select group with lowest id
        expected_group = self.user.groups.all().order_by('id').first()
        self.assertEqual(request.session['group'], expected_group)

