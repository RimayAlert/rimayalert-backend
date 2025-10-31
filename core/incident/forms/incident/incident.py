from django import forms
from core.incident.models import IncidentType, IncidentStatus


class SearchIncidentForm(forms.Form):
    type = forms.ModelChoiceField(
        queryset=IncidentType.objects.all(),
        required=False,
        label='Tipo de Incidente',
        empty_label='Todos los tipos',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    status = forms.ModelChoiceField(
        queryset=IncidentStatus.objects.all(),
        required=False,
        label='Estado',
        empty_label='Todos los estados',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
