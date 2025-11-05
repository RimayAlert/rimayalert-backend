from django import forms


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

