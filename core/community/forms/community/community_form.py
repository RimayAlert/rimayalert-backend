from django import forms
from django.contrib.gis.geos import GEOSGeometry
from core.community.models import Community


class CommunityForm(forms.ModelForm):
    boundary_area_json = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
        error_messages={
            'required': 'Debes dibujar el área límite de la comunidad en el mapa.'
        }
    )

    class Meta:
        model = Community
        fields = ['name', 'description', 'postal_code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la comunidad'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción (opcional)'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['postal_code'].required = True
        self.fields['description'].required = False

    def clean_boundary_area_json(self):
        data = self.cleaned_data.get('boundary_area_json')
        if not data:
            raise forms.ValidationError("Debes dibujar el área límite de la comunidad en el mapa.")
        try:
            geom = GEOSGeometry(data)
            if geom.geom_type != 'Polygon':
                raise forms.ValidationError("El área debe ser un polígono.")
            return geom
        except ValueError as e:
            raise forms.ValidationError(f"Geometría inválida: {e}")

    def save(self, commit=True):
        community = super().save(commit=False)
        boundary = self.cleaned_data.get('boundary_area_json')
        if boundary:
            community.boundary_area = boundary
        if commit:
            community.save()
        return community
