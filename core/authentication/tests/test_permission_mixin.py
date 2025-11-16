"""
Tests for PermissionMixin
"""
import secrets

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from django.views import View
from django.contrib.sessions.middleware import SessionMiddleware
from unittest.mock import patch

from config.mixins.permissions.permissions import PermissionMixin
from core.authentication.models import User


class DummyViewWithPermission(PermissionMixin, View):
    """Dummy view with permission requirement"""
    permission_required = 'view_group'

    def get(self, request):
        return HttpResponse('Success')


class DummyViewWithMultiplePermissions(PermissionMixin, View):
    """Dummy view with multiple permission requirements"""
    permission_required = ['view_group', 'add_group']

    def get(self, request):
        return HttpResponse('Success')


class DummyViewWithoutPermission(PermissionMixin, View):
    """Dummy view without permission requirement"""
    permission_required = ''

    def get(self, request):
        return HttpResponse('Success')


class PermissionMixinTest(TestCase):
    """Test suite for PermissionMixin"""

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

        # Create groups
        self.group_with_permission = Group.objects.create(name='GroupWithPermission')
        self.group_without_permission = Group.objects.create(name='GroupWithoutPermission')

        # Get content type for permissions
        content_type = ContentType.objects.get_for_model(Group)

        # Get existing permissions by codename only (not app_label.codename)
        self.view_permission = Permission.objects.get(
            codename='view_group',
            content_type=content_type
        )
        self.add_permission = Permission.objects.get(
            codename='add_group',
            content_type=content_type
        )

        # Add permissions to group
        self.group_with_permission.permissions.add(self.view_permission, self.add_permission)

    def _add_middleware_to_request(self, request):
        """Helper method to add session and auth middleware to request"""
        # Add session
        session_middleware = SessionMiddleware(lambda x: None)
        session_middleware.process_request(request)
        request.session.save()

        # Add authentication
        request.user = self.user

        return request

    def test_dispatch_redirects_to_login_when_user_not_authenticated(self):
        """Test dispatch redirects to login when user is not authenticated"""
        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)

        # Create anonymous user
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()

        view = DummyViewWithPermission.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 302)
        # Django's login_required redirects to login page (URL may vary based on settings)
        self.assertIn('login', response.url.lower())

    @patch('config.mixins.permissions.permissions.redirect')
    def test_dispatch_redirects_when_no_group_in_session(self, mock_redirect):
        """Test dispatch redirects when user has no group in session and no groups assigned"""
        from django.http import HttpResponseRedirect
        mock_redirect.return_value = HttpResponseRedirect('/login/')

        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)

        view = DummyViewWithPermission.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 302)
        mock_redirect.assert_called_with('authentication:login')

    def test_dispatch_allows_access_when_user_has_permission(self):
        """Test dispatch allows access when user has required permission"""
        # Add group with permission to user
        self.user.groups.add(self.group_with_permission)

        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)
        request.session['group'] = self.group_with_permission

        view = DummyViewWithPermission.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Success')

    @patch('config.mixins.permissions.permissions.redirect')
    def test_dispatch_redirects_when_user_lacks_permission(self, mock_redirect):
        """Test dispatch redirects when user doesn't have required permission"""
        from django.http import HttpResponseRedirect
        mock_redirect.return_value = HttpResponseRedirect('/login/')

        # Add group without permission to user
        self.user.groups.add(self.group_without_permission)

        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)
        request.session['group'] = self.group_without_permission

        view = DummyViewWithPermission.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 302)
        mock_redirect.assert_called_with('authentication:login')

    def test_dispatch_allows_access_when_no_permission_required(self):
        """Test dispatch allows access when no permission is required"""
        # Add any group to user
        self.user.groups.add(self.group_without_permission)

        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)
        request.session['group'] = self.group_without_permission

        view = DummyViewWithoutPermission.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Success')

    def test_dispatch_handles_multiple_permissions(self):
        """Test dispatch correctly handles multiple permission requirements"""
        # Add group with permissions to user
        self.user.groups.add(self.group_with_permission)

        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)
        request.session['group'] = self.group_with_permission

        view = DummyViewWithMultiplePermissions.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Success')

    def test_dispatch_sets_group_session_when_missing(self):
        """Test dispatch sets group session when it's missing"""
        # Add group to user
        self.user.groups.add(self.group_with_permission)

        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)
        # Don't set group in session

        view = DummyViewWithPermission.as_view()
        response = view(request)

        # Should have set the group in session
        self.assertIn('group', request.session)

    def test_dispatch_allows_partial_permissions_due_to_exists(self):
        """Test dispatch allows access when user has at least one of multiple required permissions

        This tests the ACTUAL behavior: .filter(codename__in=perms).exists()
        returns True if ANY permission matches, not ALL
        """
        # Create a group with only one permission
        group_partial = Group.objects.create(name='GroupPartialPermission')
        group_partial.permissions.add(self.view_permission)  # Only view, not add

        self.user.groups.add(group_partial)

        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)
        request.session['group'] = group_partial

        view = DummyViewWithMultiplePermissions.as_view()
        response = view(request)

        # Passes because .exists() returns True if at least one permission exists
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Success')

    def test_get_permissions_to_validate_with_string(self):
        """Test _get_permissions_to_validate with string permission"""
        view = DummyViewWithPermission()
        permissions = view._get_permissions_to_validate()

        self.assertEqual(permissions, ('view_group',))

    def test_get_permissions_to_validate_with_list(self):
        """Test _get_permissions_to_validate with list of permissions"""
        view = DummyViewWithMultiplePermissions()
        permissions = view._get_permissions_to_validate()

        self.assertEqual(permissions, ('view_group', 'add_group'))

    def test_get_permissions_to_validate_with_empty_string(self):
        """Test _get_permissions_to_validate with empty string"""
        view = DummyViewWithoutPermission()
        permissions = view._get_permissions_to_validate()

        self.assertEqual(permissions, ())

