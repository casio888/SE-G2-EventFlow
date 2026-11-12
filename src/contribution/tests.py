from django.test import TestCase

from authentication.models import Address, CustomUserOrganizer
from contribution.forms import ContributionForm
from contribution.models import Contribution
from events.models import Event


class ContributionFormTests(TestCase):
    """Test contribution form validation and saving."""

    @classmethod
    def setUpTestData(self):
        address = Address.objects.create(
            country="Deutschland",
            city="Dresden",
            street="Hochschulstraße",
            houseNbr=2,
        )
        organizer = CustomUserOrganizer.objects.create_user(
            username="HTW Dresden",
            address=address,
            telephone="0123456789",
        )
        self.event = Event.objects.create(
            event_owner=organizer,
            title="ESE",
            description="Erstsemersterwoche",
            start_date="2026-11-09",
            end_date="2026-11-10",
            location="Dresden",
        )

    @staticmethod
    def form_data(**overrides) -> dict:
        """Create valid contribution data for a test case."""
        data = {
            "duration_requested": "45",
            "description": "Test contribbution",
            "requirements": "Nothing",
        }
        data.update(overrides)
        return data

    def test_form_valid(self):
        """Accept and save a contribution with valid entries."""
        form = ContributionForm(
            event_id=self.event.pk,
            data=self.form_data(),
        )

        self.assertTrue(form.is_valid(), form.errors)
        contribution = form.save()

        self.assertEqual(Contribution.objects.count(), 1)
        self.assertEqual(contribution.fk_event, self.event)
        self.assertFalse(contribution.accepted)
        self.assertEqual(contribution.duration_requested, 45)
        self.assertEqual(contribution.description, "Test contribbution")
        self.assertEqual(contribution.requirements, "Nothing")

    def test_zero_duration_is_invalid(self):
        """Reject a contribution with no requested duration."""
        form = ContributionForm(
            event_id=self.event.pk,
            data=self.form_data(duration_requested="0"),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("duration_requested", form.errors)

    def test_negative_duration_is_invalid(self):
        """Reject a negative requested duration."""
        form = ContributionForm(
            event_id=self.event.pk,
            data=self.form_data(duration_requested="-5"),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("duration_requested", form.errors)

    def test_non_numeric_duration_is_invalid(self):
        """Reject a duration that cannot be converted to an integer."""
        form = ContributionForm(
            event_id=self.event.pk,
            data=self.form_data(duration_requested="forty-five"),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("duration_requested", form.errors)

    def test_missing_required_fields_fail(self):
        """Require a duration, description, and list of requirements."""
        # 3 Tests, each leaving one of the required fields empty
        for field_name in ("duration_requested", "description", "requirements"):
            with self.subTest(field=field_name):
                form = ContributionForm(
                    event_id=self.event.pk,
                    data=self.form_data(**{field_name: ""}),
                )

                self.assertFalse(form.is_valid())
                self.assertIn(field_name, form.errors)
