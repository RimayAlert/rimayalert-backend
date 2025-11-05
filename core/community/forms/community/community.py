from django import forms
from core.community.models import CommunityMembership


class SearchCommunityForm(forms.Form):
    is_active = forms.NullBooleanField(
        required=False,
        label='Estado',
        widget=forms.Select(
            choices=[
                ('', 'Todas'),
                ('true', 'Activas'),
                ('false', 'Inactivas'),
            ],
            attrs={'class': 'form-select'}
        )
    )

    postal_code = forms.CharField(
        required=False,
        label='Código Postal',
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por código postal'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SearchMemberForm(forms.Form):
    role = forms.ChoiceField(
        required=False,
        label='Rol',
        choices=[('', 'Todos los roles')] + list(CommunityMembership.ROLE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    is_verified = forms.NullBooleanField(
        required=False,
        label='Estado de verificación',
        widget=forms.Select(
            choices=[
                ('', 'Todos'),
                ('true', 'Verificados'),
                ('false', 'No verificados'),
            ],
            attrs={'class': 'form-select'}
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


