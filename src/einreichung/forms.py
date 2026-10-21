from django import forms

from .models import Einreichung
from veranstaltungen.models import Timeslot
from veranstaltungen.utils import get_event


class EinreichungForm(forms.ModelForm):
    """
    Form to create applications to events (event timeslots)
    """
    class Meta:
        model = Einreichung
        fields = ["duration_requested", "Beschreibung", "Anforderungen"]

    def __init__(self, *args, event_id, **kwargs):
        super().__init__(*args, **kwargs)
        veranstaltung = get_event(event_id)
        self.instance.fk = veranstaltung
        self.fields["timeslot"] = forms.ModelChoiceField(
            queryset=Timeslot.objects.filter(veranstaltung=veranstaltung),
            label="Timeslot",
        )

    def clean(self):
        cleaned_data = super().clean()
        duration = cleaned_data.get("duration_requested")
        timeslot = cleaned_data.get("timeslot")

        if duration is not None and timeslot is not None:
            if duration <= 0:
                raise  forms.ValidationError({"duration": "Die Dauer muss größer 0 Minuten sein."})
            if duration > timeslot.dauer:
                raise forms.ValidationError({"duration": "Die Dauer darf nicht größer als der Zeitslot sein."})

        self.instance.eingereicht = True
        self.instance.fk_timeslot = timeslot
        return cleaned_data
