import json
from datetime import datetime

from django import forms
from django.conf import settings
from django.utils import timezone

from .models import Event
from .utils import _add_calendar_years


class EventForm(forms.ModelForm):
    """Form for creating and editing events.

    Contains a hidden JSON field for timeslots that are added dynamically
    with JavaScript.
    """

    timeslots = forms.CharField(widget=forms.HiddenInput(), required=False)

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
            "location": forms.TextInput(attrs={"placeholder": "Venue / Ort"}),
        }

    def clean_timeslots(self):
        """Validate and normalize the timeslot JSON.

        Checks:
        - Time format
        - Start < end
        - Duration > 0
        - Category is present

        Returns:
            list[dict]: Cleaned timeslot data
        """
        raw = self.cleaned_data["timeslots"]
        if not raw:
            return []

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            raise forms.ValidationError("Timeslots konnten nicht verarbeitet werden.")

        cleaned = []

        for slot in data:
            start = slot.get("start")
            end = slot.get("end")
            duration = slot.get("duration")
            category = slot.get("category")

            if not start or not end:
                raise forms.ValidationError("Start und Ende müssen ausgefüllt sein.")

            try:
                t_start = datetime.strptime(start, "%H:%M")
                t_end = datetime.strptime(end, "%H:%M")
            except ValueError:
                raise forms.ValidationError("Ungültiges Zeitformat. Bitte HH:MM verwenden.")

            if t_start >= t_end:
                raise forms.ValidationError("Startzeit muss vor der Endzeit liegen.")

            if duration:
                try:
                    duration_int = int(duration)
                    if duration_int <= 0:
                        raise forms.ValidationError("Dauer muss größer als 0 sein.")
                except ValueError:
                    raise forms.ValidationError("Dauer muss eine Zahl sein.")
            else:
                duration_int = int((t_end - t_start).seconds / 60)

            if not category:
                raise forms.ValidationError("Kategorie darf nicht leer sein.")

            cleaned.append(
                {
                    "start": start,
                    "end": end,
                    "duration": duration_int,
                    "category": category,
                }
            )

        return cleaned

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date is None and end_date is None:
            return cleaned_data

        today = timezone.localdate()
        latest_date = _add_calendar_years(
            today, settings.MAX_EVENT_YEARS_IN_FUTURE
        )

        if start_date is not None:
            existing_start_date = None
            if self.instance.pk:
                existing_start_date = self.instance.start_date

            unchanged_past_start_date = (
                start_date == existing_start_date and start_date < today
            )

            if start_date < today and not unchanged_past_start_date:
                self.add_error(
                    "start_date",
                    "Das Startdatum darf nicht in der Vergangenheit liegen.",
                )

            if start_date > latest_date:
                self.add_error(
                    "start_date",
                    "Das Startdatum darf höchstens fünf Kalenderjahre in der Zukunft liegen.",
                )

        if end_date is not None and end_date > latest_date:
            self.add_error(
                "end_date",
                "Das Enddatum darf höchstens fünf Kalenderjahre in der Zukunft liegen.",
            )

        if start_date is None or end_date is None:
            return cleaned_data

        if start_date > end_date:
            self.add_error(
                "end_date",
                "Das Enddatum muss am oder nach dem Startdatum liegen.",
            )

        return cleaned_data

    def save(self, commit=True):
        """Save the event and create its associated timeslots.

        Returns:
            Event: Saved event instance
        """
        event = super().save(commit)

        from .models import Timeslot

        slots = self.cleaned_data.get("timeslots", [])
        for slot in slots:
            Timeslot.objects.create(
                event=event,
                start=datetime.strptime(slot["start"], "%H:%M").time(),
                end=datetime.strptime(slot["end"], "%H:%M").time(),
                duration=slot["duration"],
                category=slot["category"],
            )

        return event
