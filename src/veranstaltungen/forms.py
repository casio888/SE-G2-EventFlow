import json
from datetime import date, datetime

from django import forms
from django.utils import timezone

from .models import Veranstaltung


# Vorläufige fachliche Grenze, bis die Abstimmung mit dem Team erfolgt ist.
MAX_EVENT_YEARS_IN_FUTURE = 5


def _add_calendar_years(value: date, years: int) -> date:
    """Addiert Kalenderjahre zu einem Datum.

    Der 29. Februar wird in einem Zieljahr ohne Schalttag auf den
    28. Februar abgebildet.

    Arguments:
        value {date} -- Ausgangsdatum
        years {int} -- Anzahl der zu addierenden Kalenderjahre

    Returns:
        date -- Datum im entsprechenden Zieljahr
    """
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(year=value.year + years, day=28)


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
            "start_datum": forms.DateInput(
                attrs={
                    "placeholder": "17.06.2026",
                    "onfocus": "(this.type='date')",
                    "onblur": "if(!this.value)this.type='text'",
                }
            ),
            "end_datum": forms.DateInput(
                attrs={
                    "placeholder": "17.06.2026",
                    "onfocus": "(this.type='date')",
                    "onblur": "if(!this.value)this.type='text'",
                }
            ),
            "titel": forms.TextInput(attrs={"placeholder": "[Event Name]"}),
            "beschreibung": forms.Textarea(
                attrs={
                    "placeholder": "[Catch Phrase / Beschreibung]",
                    "rows": 3,
                }
            ),
            "ort": forms.TextInput(attrs={"placeholder": "Venue / Ort"}),
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

            cleaned.append(
                {
                    "start": start,
                    "ende": ende,
                    "dauer": dauer_int,
                    "kategorie": kategorie,
                }
            )

        return cleaned

    def clean(self):
        cleaned_data = super().clean()

        start_datum = cleaned_data.get("start_datum")
        end_datum = cleaned_data.get("end_datum")
        heute = timezone.localdate()
        spaetestes_datum = _add_calendar_years(heute, MAX_EVENT_YEARS_IN_FUTURE)

        bestehendes_startdatum = None
        if self.instance.pk:
            bestehendes_startdatum = self.instance.start_datum

        vergangenes_startdatum_ist_unveraendert = (
            start_datum is not None
            and start_datum == bestehendes_startdatum
            and start_datum < heute
        )

        if (
            start_datum
            and start_datum < heute
            and not vergangenes_startdatum_ist_unveraendert
        ):
            self.add_error(
                "start_datum",
                "Das Startdatum darf nicht in der Vergangenheit liegen.",
            )

        if start_datum and start_datum > spaetestes_datum:
            self.add_error(
                "start_datum",
                "Das Startdatum darf höchstens fünf Kalenderjahre in der Zukunft liegen.",
            )

        if end_datum and end_datum > spaetestes_datum:
            self.add_error(
                "end_datum",
                "Das Enddatum darf höchstens fünf Kalenderjahre in der Zukunft liegen.",
            )

        if start_datum and end_datum and start_datum > end_datum:
            self.add_error(
                "end_datum",
                "Das Enddatum muss am oder nach dem Startdatum liegen.",
            )

        return cleaned_data

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
                start=datetime.strptime(slot["start"], "%H:%M").time(),
                ende=datetime.strptime(slot["ende"], "%H:%M").time(),
                dauer=slot["dauer"],
                kategorie=slot["kategorie"],
            )

        return veranstaltung
