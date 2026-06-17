from django import forms

from .models import User


class RegistrierungsForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Passwort", "maxlength": 100}),
        label="Passwort",
    )

    class Meta:
        model = User
        fields = [
            "firmenname",
            "firmensitzLand",
            "firmensitzOrt",
            "firmensitzStraße",
            "firmensitzHausnummer",
            "email",
            "password",
            "telefon",
            "fax",
        ]
        labels = {
            "firmenname": "Firmenname",
            "firmensitzLand": "Land",
            "firmensitzOrt": "Stadt",
            "firmensitzStraße": "Straße",
            "firmensitzHausnummer": "Hausnummer",
            "email": "E-Mail",
            "telefon": "Telefonnummer",
            "fax": "Fax",
        }
        widgets = {
            "firmenname": forms.TextInput(attrs={"placeholder": "Firmenname", "maxlength": 200}),
            "firmensitzLand": forms.TextInput(attrs={"placeholder": "Land", "maxlength": 50}),
            "firmensitzOrt": forms.TextInput(attrs={"placeholder": "Stadt", "maxlength": 170}),
            "firmensitzStraße": forms.TextInput(attrs={"placeholder": "Straße", "maxlength": 85}),
            "firmensitzHausnummer": forms.NumberInput(attrs={"placeholder": "Hausnummer", "min": 1}),
            "email": forms.EmailInput(attrs={"placeholder": "E-Mail", "maxlength": 160}),
            "telefon": forms.TextInput(attrs={"placeholder": "Telefonnummer", "maxlength": 15}),
            "fax": forms.TextInput(attrs={"placeholder": "Fax", "maxlength": 15}),
        }
