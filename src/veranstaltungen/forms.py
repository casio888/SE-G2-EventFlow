from django import forms
from .models import Veranstaltung

class VeranstaltungForm(forms.ModelForm):
    class Meta:
        model = Veranstaltung
        fields = ["titel", "beschreibung", "start_datum", "end_datum", "ort"]

        widgets = {
            "titel": forms.TextInput(attrs={"class": "form-control"}),
            "beschreibung": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "start_datum": forms.DateInput(attrs={"class": "form-control", "type":"date"}),
            "end_datum": forms.DateInput(attrs={"class": "form-control", "type":"date"}),
            "ort": forms.TextInput(attrs={"class": "form-control"}),
        }
