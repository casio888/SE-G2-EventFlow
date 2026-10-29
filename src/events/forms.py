from datetime import date, datetime

from django import forms
from django.conf import settings
from django.forms import inlineformset_factory
from django.utils import timezone

from .models import Event, Timeslot
from .utils import _add_calendar_years


class TimeslotForm(forms.ModelForm):
    """Create or update a timeslot for an existing event."""

    class Meta:
        model = Timeslot
        fields = ["category", "start", "end"]
        labels = {
            "category": "Kategorie",
            "start": "Startzeit",
            "end": "Endzeit",
        }
        error_messages = {
            "category": {"required": "Kategorie darf nicht leer sein."},
            "start": {"required": "Startzeit muss ausgefüllt sein."},
            "end": {"required": "Endzeit muss ausgefüllt sein."},
        }

    def clean(self):
        """Ensure that the timeslot ends after it starts."""
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")

        if start and end and start >= end:
            self.add_error("end", "Startzeit muss vor der Endzeit liegen.")

        return cleaned_data

    def save(self, commit=True):
        """Save the timeslot with a duration matching its time range."""
        timeslot = super().save(commit=False)
        start_datetime = datetime.combine(date.min, timeslot.start)
        end_datetime = datetime.combine(date.min, timeslot.end)
        timeslot.duration = int(
            (end_datetime - start_datetime).total_seconds() / 60
        )

        if commit:
            timeslot.save()

        return timeslot


class EventForm(forms.ModelForm):
    """Form for creating and editing events."""

    class Meta:
        model = Event
        fields = ["title", "description", "location", "start_date", "end_date"]

        widgets = {
            "start_date": forms.DateInput(
                attrs={
                    "placeholder": "17.06.2026",
                    "onfocus": "(this.type='date')",
                    "onblur": "if(!this.value)this.type='text'",
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "placeholder": "17.06.2026",
                    "onfocus": "(this.type='date')",
                    "onblur": "if(!this.value)this.type='text'",
                }
            ),
            "title": forms.TextInput(attrs={"placeholder": "[Event Name]"}),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "[Catch Phrase / Beschreibung]",
                    "rows": 3,
                }
            ),
            "location": forms.TextInput(attrs={"placeholder": "Ort"}),
        }

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        today = timezone.localdate()
        latest_date = _add_calendar_years(
            today, settings.MAX_EVENT_YEARS_IN_FUTURE
        )

        # Validate the start date.
        if start_date:
            start_date_unchanged = (
                self.instance.pk
                and start_date == self.instance.start_date
            )

            if start_date < today and not start_date_unchanged:
                self.add_error(
                    "start_date",
                    "Das Startdatum darf nicht in der Vergangenheit liegen.",
                )

            if start_date > latest_date:
                self.add_error(
                    "start_date",
                    "Das Startdatum darf höchstens fünf Kalenderjahre in der Zukunft liegen.",
                )

        # Validate the end date.
        if end_date:
            if end_date > latest_date:
                self.add_error(
                    "end_date",
                    "Das Enddatum darf höchstens fünf Kalenderjahre in der Zukunft liegen.",
                )

        # Validate the date order.
        if start_date and end_date:
            if start_date > end_date:
                self.add_error(
                    "end_date",
                    "Das Enddatum muss am oder nach dem Startdatum liegen.",
                )

        return cleaned_data


TimeslotFormSet = inlineformset_factory(
    Event,
    Timeslot,
    form=TimeslotForm,
    extra=0,
    can_delete=False,
)
