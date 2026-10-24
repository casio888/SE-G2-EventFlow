from django import forms

from .models import Contribution
from events.utils import get_event

class ContributionForm(forms.ModelForm):
    """
    Form to create applications to events (event timeslots)
    """
    class Meta:
        model = Contribution
        fields = ["duration_requested", "description", "requirements"]

    def __init__(self, *args, event_id, **kwargs):
        super().__init__(*args, **kwargs)
        event = get_event(event_id)
        self.instance.fk = event

    def clean(self):
        cleaned_data = super().clean()
        duration = cleaned_data.get("duration_requested")

        if duration is not None:
            if duration <= 0:
                raise  forms.ValidationError({"duration": "Die Dauer muss größer 0 Minuten sein."})
        else:
            raise forms.ValidationError({"duration": "Es muss eine dauer angegeben werden."})

        self.instance.eingereicht = True
        return cleaned_data