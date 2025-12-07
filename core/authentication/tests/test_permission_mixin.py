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
    permission_required = 'view_group'

    def get(self, request):
        return HttpResponse('Success')


class DummyViewWithMultiplePermissions(PermissionMixin, View):
    permission_required = ['view_group', 'add_group']

    def get(self, request):
        return HttpResponse('Success')


class DummyViewWithoutPermission(PermissionMixin, View):
    permission_required = ''

    def get(self, request):
        return HttpResponse('Success')


class PermissionMixinTest(TestCase):

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

        self.group_with_permission = Group.objects.create(name='GroupWithPermission')
        self.group_without_permission = Group.objects.create(name='GroupWithoutPermission')
        content_type = ContentType.objects.get_for_model(Group)
        self.view_permission = Permission.objects.get(
            codename='view_group',
            content_type=content_type
        )
        self.add_permission = Permission.objects.get(
            codename='add_group',
            content_type=content_type
        )

        self.group_with_permission.permissions.add(self.view_permission, self.add_permission)

    def _add_middleware_to_request(self, request):
        session_middleware = SessionMiddleware(lambda x: None)
        session_middleware.process_request(request)
        request.session.save()

        request.user = self.user

        return request

    def test_dispatch_redirects_to_login_when_user_not_authenticated(self):
        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)

        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()

        view = DummyViewWithPermission.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url.lower())

    @patch('config.mixins.permissions.permissions.redirect')
    def test_dispatch_redirects_when_no_group_in_session(self, mock_redirect):
        from django.http import HttpResponseRedirect
        mock_redirect.return_value = HttpResponseRedirect('/login/')

        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)

        view = DummyViewWithPermission.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 302)
        mock_redirect.assert_called_with('authentication:login')

    def test_dispatch_allows_access_when_user_has_permission(self):
        self.user.groups.add(self.group_with_permission)

        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)
        request.session['group_id'] = self.group_with_permission.id

        view = DummyViewWithPermission.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Success')

    @patch('config.mixins.permissions.permissions.redirect')
    def test_dispatch_redirects_when_user_lacks_permission(self, mock_redirect):
        from django.http import HttpResponseRedirect
        mock_redirect.return_value = HttpResponseRedirect('/login/')

        self.user.groups.add(self.group_without_permission)

        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)
        request.session['group_id'] = self.group_without_permission.id

        view = DummyViewWithPermission.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 302)
        mock_redirect.assert_called_with('authentication:login')

    def test_dispatch_allows_access_when_no_permission_required(self):
        self.user.groups.add(self.group_without_permission)

        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)
        request.session['group_id'] = self.group_without_permission.id

        view = DummyViewWithoutPermission.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Success')

    def test_dispatch_handles_multiple_permissions(self):
        self.user.groups.add(self.group_with_permission)

        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)
        request.session['group_id'] = self.group_with_permission.id

        view = DummyViewWithMultiplePermissions.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Success')

    def test_dispatch_sets_group_session_when_missing(self):
        self.user.groups.add(self.group_with_permission)

        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)

        view = DummyViewWithPermission.as_view()
        response = view(request)

        self.assertIn('group_id', request.session)

    def test_dispatch_allows_partial_permissions_due_to_exists(self):
        group_partial = Group.objects.create(name='GroupPartialPermission')
        group_partial.permissions.add(self.view_permission)  # Only view, not add

        self.user.groups.add(group_partial)

        request = self.factory.get('/')
        request = self._add_middleware_to_request(request)
        request.session['group_id'] = group_partial.id

        view = DummyViewWithMultiplePermissions.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Success')

    def test_get_permissions_to_validate_with_string(self):
        view = DummyViewWithPermission()
        permissions = view._get_permissions_to_validate()

        self.assertEqual(permissions, ('view_group',))

    def test_get_permissions_to_validate_with_list(self):
        view = DummyViewWithMultiplePermissions()
        permissions = view._get_permissions_to_validate()

        self.assertEqual(permissions, ('view_group', 'add_group'))

    def test_get_permissions_to_validate_with_empty_string(self):
        view = DummyViewWithoutPermission()
        permissions = view._get_permissions_to_validate()

        self.assertEqual(permissions, ())

