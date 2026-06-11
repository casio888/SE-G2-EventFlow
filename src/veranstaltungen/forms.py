from django import forms
from .models import Veranstaltung
import json
from datetime import datetime

class VeranstaltungForm(forms.ModelForm):
    """
    Formular zur Erstellung und Bearbeitung von Veranstaltungen.

    Enthält ein verstecktes JSON-Feld für Timeslots, die per JavaScript
    dynamisch hinzugefügt werden.
    """
    timeslots = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Veranstaltung
        fields = ["titel", "beschreibung", "ort", "start_datum", "end_datum"]
        
        widgets = {
<<<<<<< HEAD
        "start_datum": forms.DateInput(attrs={
        "placeholder": "17.06.2026", 
        "onfocus": "(this.type='date')", 
        "onblur": "if(!this.value)this.type='text'"
    }),
    "end_datum": forms.DateInput(attrs={
        "placeholder": "17.06.2026", 
        "onfocus": "(this.type='date')", 
        "onblur": "if(!this.value)this.type='text'"
    }),
            
    
        "titel": forms.TextInput(attrs={"placeholder": "[Event Name]"}),
        "beschreibung": forms.Textarea(attrs={"placeholder": "[Catch Phrase / Beschreibung]", "rows": 3}),
        "ort": forms.TextInput(attrs={"placeholder": "Venue / Ort"}),
=======
            "titel": forms.TextInput(attrs={"class": "form-control"}),
            "beschreibung": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "start_datum": forms.DateInput(attrs={"class": "form-control", "type":"date"}),
            "end_datum": forms.DateInput(attrs={"class": "form-control", "type":"date"}),
            "ort": forms.TextInput(attrs={"class": "form-control"}),
>>>>>>> d8e4f2d (feature: add event editing)
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
            ende = slot.get("ende")
            dauer = slot.get("dauer")
            kategorie = slot.get("kategorie")

            if not start or not ende:
                raise forms.ValidationError("Start und Ende müssen ausgefüllt sein.")

            try:
                t_start = datetime.strptime(start, "%H:%M")
                t_ende = datetime.strptime(ende, "%H:%M")
            except ValueError:
                raise forms.ValidationError("Ungültiges Zeitformat. Bitte HH:MM verwenden.")

            if t_start >= t_ende:
                raise forms.ValidationError("Startzeit muss vor der Endzeit liegen.")

            if dauer:
                try:
                    dauer_int = int(dauer)
                    if dauer_int <= 0:
                        raise forms.ValidationError("Dauer muss größer als 0 sein.")
                except ValueError:
                    raise forms.ValidationError("Dauer muss eine Zahl sein.")
            else:
                dauer_int = int((t_ende - t_start).seconds / 60)

            if not kategorie:
                raise forms.ValidationError("Kategorie darf nicht leer sein.")

            cleaned.append({
                "start": start,
                "ende": ende,
                "dauer": dauer_int,
                "kategorie": kategorie
            })

        return cleaned

    def save(self, commit=True):
        """
        Speichert die Veranstaltung und erzeugt zugehörige Timeslots.

        Returns:
            Veranstaltung: Gespeichertes Veranstaltungsobjekt
        """
        veranstaltung = super().save(commit)

        from .models import Timeslot

        slots = self.cleaned_data.get("timeslots", [])
        for slot in slots:
            Timeslot.objects.create(
                veranstaltung=veranstaltung,
                start=slot["start"],
                ende=slot["ende"],
                dauer=slot["dauer"],
                kategorie=slot["kategorie"],
            )

<<<<<<< HEAD
        return veranstaltung
=======
        return veranstaltung
>>>>>>> d8e4f2d (feature: add event editing)
