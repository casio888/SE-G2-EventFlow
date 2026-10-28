from django import forms
from .models import Event
import json
from datetime import datetime

class EventForm(forms.ModelForm):
    """
    Formular zur Erstellung und Bearbeitung von Veranstaltungen.

    Enthält ein verstecktes JSON-Feld für Timeslots, die per JavaScript
    dynamisch hinzugefügt werden.
    """
    timeslots = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Event
        fields = ["title", "description", "location", "start_date", "end_date"]
        
        widgets = {
        "start_date": forms.DateInput(attrs={
        "placeholder": "17.06.2026", 
        "onfocus": "(this.type='date')", 
        "onblur": "if(!this.value)this.type='text'"
    }),
    "end_date": forms.DateInput(attrs={
        "placeholder": "17.06.2026", 
        "onfocus": "(this.type='date')", 
        "onblur": "if(!this.value)this.type='text'"
    }),
            
    
        "title": forms.TextInput(attrs={"placeholder": "[Event Name]"}),
        "description": forms.Textarea(attrs={"placeholder": "[Catch Phrase / Beschreibung]", "rows": 3}),
        "location": forms.TextInput(attrs={"placeholder": "Venue / Ort"}),
        }

    def clean_timeslots(self):
        """
        Validiert das Timeslot-JSON.

        Prüft:
        - Zeitformat
        - Start < Ende
        - Dauer > 0
        - Kategorie vorhanden

        Returns:
            list[dict]: Bereinigte Timeslot-Daten
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

            cleaned.append({
                "start": start,
                "end": end,
                "duration": duration_int,
                "category": category
            })

        return cleaned

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError({
                "end_date": "Das Enddatum muss am oder nach dem Startdatum liegen."
            })

        return cleaned_data

    def save(self, commit=True):
        """
        Speichert die Veranstaltung und erzeugt zugehörige Timeslots.

        Returns:
            Event: Gespeichertes Veranstaltungsobjekt
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
