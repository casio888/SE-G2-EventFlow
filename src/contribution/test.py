from datetime import date

from django.test import TestCase
from django.urls import reverse

from events.models import Event
from authentication.models import Address, CustomUserContributer, CustomUserOrganizer
from contribution.models import Contribution
from contribution.views import get_contributions_for_event


class ContributionTestMixin:

    @classmethod
    def setUpTestData(cls):
        # 1. Adresse (Felder an dein Address-Modell anpassen)
        cls.address = Address.objects.create(
            country="Testland",
            city="testcity",
            street="teststreet",
            houseNbr="1",
        )

        # 2. Benutzer (create_user hasht das Passwort korrekt)
        cls.organizer = CustomUserOrganizer.objects.create_user(
            username="organizer",
            password="test12345",
            address=cls.address,
            telephone="0341123456",
        )
        cls.user = CustomUserContributer.objects.create_user(
            username="tester",
            password="test12345",
            address=cls.address,
            telephone="0341654321",
        )

        # 3. Events
        cls.event = Event.objects.create(
            event_owner=cls.organizer,
            title="Testevent",
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 2),
            location="Leipzig",
        )
        cls.andere_event = Event.objects.create(
            event_owner=cls.organizer,
            title="Anderes Event",
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 2),
            location="Dresden",
        )

    def create_contribution(self, event, submitted=False, description="Beschreibung"):
        return Contribution.objects.create(
            event=event,
            contributer=self.user,
            submitted=submitted,
            description=description,
            requirements="Anforderungen",
        )


class ContributionModelTests(ContributionTestMixin, TestCase):

    def test_contribution_safe(self):
        contribution = self.create_contribution(self.event, submitted=True)
        self.assertEqual(contribution.event, self.event)
        self.assertEqual(contribution.contributer, self.user)
        self.assertTrue(contribution.submitted)
        self.assertEqual(Contribution.objects.count(), 1)

    def test_remove_event(self):
        self.create_contribution(self.event)
        self.event.delete()
        self.assertEqual(Contribution.objects.count(), 0)


class GetContributionsForEventTests(ContributionTestMixin, TestCase):

    def test_only_contributions_of_this_event(self):
        c1 = self.create_contribution(self.event)
        c2 = self.create_contribution(self.event)
        self.create_contribution(self.andere_event)

        ergebnis = get_contributions_for_event(self.event.id)

        self.assertEqual(set(ergebnis), {c1, c2})
        self.assertEqual(ergebnis.count(), 2)

    def test_no_contributions(self):
        ergebnis = get_contributions_for_event(self.event.id)
        self.assertFalse(ergebnis.exists())

    def test_unknown_id(self):
        ergebnis = get_contributions_for_event(99999)
        self.assertFalse(ergebnis.exists())


class EventContributionsViewTests(ContributionTestMixin, TestCase):

    def setUp(self):
        # Passe den URL-Namen an deine urls.py an,
        # z. B. 'event_contributions' oder 'contribution:event_contributions'.
        self.url = lambda event_id: reverse("event_contribution_list", args=[event_id])

    def test_404_unknown_event(self):
        response = self.client.get(self.url(99999))
        self.assertEqual(response.status_code, 404)


# Create your tests here.
