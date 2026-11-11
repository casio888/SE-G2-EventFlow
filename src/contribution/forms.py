from django import forms

from .models import Contribution
from events.utils import get_event

class ContributionForm(forms.ModelForm):
    """
    Form to create applications to events
    """
    class Meta:
        model = Contribution
        fields = ["duration_requested", "description", "requirements"]

    def __init__(self, *args, event_id, **kwargs):
        super().__init__(*args, **kwargs)
        event = get_event(event_id)
        self.instance.fk_event = event
        self.instance.accepted = False

    def clean(self):
        cleaned_data = super().clean()
        duration = cleaned_data.get("duration_requested")

        if duration is not None:
            if duration <= 0:
                raise forms.ValidationError({"duration_requested": "Die Dauer muss größer 0 Minuten sein."})
        elif not self.has_error("duration_requested"):
            raise forms.ValidationError({"duration_requested": "Es muss eine Dauer angegeben werden."})

        return cleaned_data

    def save(self, contributor=None, commit=True):
        contribution = super.save(commit=False)
        if contributor is not None:
            contribution.fk_contributor = contributor
        else:
            raise ValueError("Der Nutzeraccount muss ein Einreicher sein um sich auf Events zu bewerben.")

        if commit:
            contribution.save()

        return contribution