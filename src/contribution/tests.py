from django.test import RequestFactory, TestCase
from django.urls import reverse

from base.utils import redirect_to_referrer
from authentication.models import Address, CustomUserContributer, CustomUserOrganizer
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
        self.contributor = CustomUserContributer.objects.create_user(
            username="Test Contributor",
            address=address,
            telephone="0123456789",
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
            event=self.event,
            data=self.form_data(),
        )

        self.assertTrue(form.is_valid(), form.errors)
        contribution = form.save(contributor=self.contributor)

        self.assertEqual(Contribution.objects.count(), 1)
        self.assertEqual(contribution.fk_event, self.event)
        self.assertFalse(contribution.accepted)
        self.assertEqual(contribution.duration_requested, 45)
        self.assertEqual(contribution.description, "Test contribbution")
        self.assertEqual(contribution.requirements, "Nothing")

    def test_zero_duration_is_invalid(self):
        """Reject a contribution with no requested duration."""
        form = ContributionForm(
            event=self.event,
            data=self.form_data(duration_requested="0"),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("duration_requested", form.errors)

    def test_negative_duration_is_invalid(self):
        """Reject a negative requested duration."""
        form = ContributionForm(
            event=self.event,
            data=self.form_data(duration_requested="-5"),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("duration_requested", form.errors)

    def test_non_numeric_duration_is_invalid(self):
        """Reject a duration that cannot be converted to an integer."""
        form = ContributionForm(
            event=self.event,
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
                    event=self.event,
                    data=self.form_data(**{field_name: ""}),
                )

                self.assertFalse(form.is_valid())
                self.assertIn(field_name, form.errors)

    def test_error_on_duplicate_contribution(self):
        Contribution.objects.create(
            fk_event=self.event,
            fk_contributor=self.contributor,
            accepted=False,
            duration_requested=45,
            description="Existing contribution",
            requirements="Nothing",
        )
        self.client.force_login(self.contributor)
        application_url = reverse(
            "event_application",
            kwargs={"event_id": self.event.pk},
        )

        response = self.client.post(
            application_url,
            self.form_data(),
            HTTP_REFERER=application_url,
        )

        self.assertRedirects(
            response,
            reverse("event_list"),
            fetch_redirect_response=False,
        )
        landing_page = self.client.get(response.url)
        self.assertTrue(
            any(
                "error" in message.tags.split()
                for message in landing_page.context["messages"]
            ),
            "Expected an error message on the referrer page.",
        )
        self.assertEqual(Contribution.objects.count(), 1)

    def test_referrer_redirect_uses_generic_fallback_target(self):
        request = RequestFactory().get("/current-page/", HTTP_REFERER="/current-page/")

        response = redirect_to_referrer(request, "/fallback-page/")

        self.assertEqual(response.url, "/fallback-page/")
