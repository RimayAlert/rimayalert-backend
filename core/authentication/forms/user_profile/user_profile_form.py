from django import forms
from django.contrib.gis.geos import Point
from core.authentication.models import UserProfile


class UserProfileForm(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = UserProfile
        fields = ['bio', 'alias_name', 'latitude', 'longitude']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Cuéntanos sobre ti...'}),
            'alias_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alias'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('latitude')
        lng = cleaned_data.get('longitude')
        
        if lat is not None and lng is not None:
            cleaned_data['location'] = Point(lng, lat, srid=4326)
            
        return cleaned_data

    def save(self, commit=True):
        profile = super().save(commit=False)
        if 'location' in self.cleaned_data:
            profile.location = self.cleaned_data['location']
        if commit:
            profile.save()
        return profile
