from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator

class PermissionMixin(object):
    permission_required = ''

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        try:
            user = request.user
            user.set_group_session(request)
            
            if 'group_id' not in request.session:
                return redirect('authentication:login')
        
            group = user.get_group_session(request)
        
            if not group:
                return redirect('authentication:login')
        
            permissions_to_validate = self._get_permissions_to_validate()
        
            if not len(permissions_to_validate):
                return super().dispatch(request, *args, **kwargs)

            has_permission = group.permissions.filter(codename__in=permissions_to_validate).exists()
        
            if has_permission:
                return super().dispatch(request, *args, **kwargs)

            return redirect('authentication:login')
        
        except Exception as e:
            return redirect('authentication:login')

    def _get_permissions_to_validate(self):
        if self.permission_required == '':
            return ()

        if isinstance(self.permission_required, str):
            return (self.permission_required,)

        return tuple(self.permission_required)