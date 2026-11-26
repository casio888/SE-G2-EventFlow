from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from base.utils import redirect_to_referrer
from authentication.models import Address, CustomUserContributer, CustomUserOrganizer
from contribution.forms import ContributionForm
from contribution.models import Contribution
from contribution.utils import get_decision_status, get_contributions_for_event
from events.models import Event
from datetime import date


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
        self.assertEqual(contribution.status, Contribution.Status.PENDING)
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
            status=Contribution.Status.PENDING,
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

    # Tests for get_decision_status function


class DecisionStatusTests(TestCase):
    def test_get_decision_status_returns_accepted_for_accept(self):
        """Return the accepted status for the accept action.

        Args:
            self (DecisionStatusTests): Current test case instance.

        Returns:
            None: The expected status is checked by an assertion.
        """
        status = get_decision_status("accept")

        self.assertEqual(status, Contribution.Status.ACCEPTED)

    def test_get_decision_status_returns_rejected_for_reject(self):
        """Return the rejected status for the reject action.

        Args:
            self (DecisionStatusTests): Current test case instance.

        Returns:
            None: The expected status is checked by an assertion.
        """
        status = get_decision_status("reject")

        self.assertEqual(status, Contribution.Status.REJECTED)

    def test_get_decision_status_returns_none_for_unknown_action(self):
        """Return no status for an unsupported action.

        Args:
            self (DecisionStatusTests): Current test case instance.

        Returns:
            None: The missing status is checked by an assertion.
        """
        status = get_decision_status("invalid")

        self.assertIsNone(status)

#=======================
# test by @El-Assassin
#=======================
class ContributionTestMixin:
    @classmethod
    def setUpTestData(cls):
        cls.address = Address.objects.create(
            country="Deutschland",
            city="Dresden",
            street="Teststraße",
            houseNbr=1,
        )
        cls.organizer = CustomUserOrganizer.objects.create_user(
            username="organizer",
            password="test12345",
            address=cls.address,
            telephone="0341123456",
        )
        cls.other_organizer = CustomUserOrganizer.objects.create_user(
            username="other-organizer",
            password="test12345",
            address=cls.address,
            telephone="0341123457",
        )
        cls.contributor = CustomUserContributer.objects.create_user(
            username="contributor",
            password="test12345",
            address=cls.address,
            telephone="0341654321",
        )
        cls.event = cls.create_event(
            cls.organizer,
            "Erstes Event",
            date(2026, 12, 1),
        )
        cls.other_event = cls.create_event(
            cls.organizer,
            "Zweites Event",
            date(2026, 12, 2),
        )
        cls.foreign_event = cls.create_event(
            cls.other_organizer,
            "Fremdes Event",
            date(2026, 12, 3),
        )

    @staticmethod
    def create_event(organizer, title, start_date):
        return Event.objects.create(
            event_owner=organizer,
            title=title,
            start_date=start_date,
            end_date=start_date,
            location="Dresden",
        )

    def create_contribution(
        self,
        event,
        status=Contribution.Status.PENDING,
        description="Beschreibung",
    ):
        return Contribution.objects.create(
            fk_event=event,
            fk_contributor=self.contributor,
            status=status,
            duration_requested=45,
            description=description,
            requirements="Beamer",
        )


class ContributionModelTests(ContributionTestMixin, TestCase):
    def test_status_choices_contain_all_application_states(self):
        self.assertEqual(
            set(Contribution.Status.values),
            {"pending", "accepted", "rejected"},
        )
        self.assertEqual(Contribution.Status.PENDING.label, "Offen")
        self.assertEqual(Contribution.Status.ACCEPTED.label, "Angenommen")
        self.assertEqual(Contribution.Status.REJECTED.label, "Abgelehnt")

    def test_new_contribution_defaults_to_pending(self):
        contribution = Contribution.objects.create(
            fk_event=self.event,
            fk_contributor=self.contributor,
            duration_requested=30,
            description="Vortrag",
            requirements="Keine",
        )

        self.assertEqual(contribution.status, Contribution.Status.PENDING)

    def test_each_status_can_be_stored(self):
        for status in Contribution.Status.values:
            with self.subTest(status=status):
                contribution = self.create_contribution(self.event, status=status)
                contribution.refresh_from_db()
                self.assertEqual(contribution.status, status)

    def test_deleting_event_deletes_its_contributions(self):
        self.create_contribution(self.event)

        self.event.delete()

        self.assertEqual(Contribution.objects.count(), 0)


class ContributionApplicationTests(ContributionTestMixin, TestCase):
    def test_contributor_can_create_pending_application(self):
        self.client.force_login(self.contributor)

        response = self.client.post(
            reverse("event_application", args=[self.event.pk]),
            {
                "duration_requested": 60,
                "description": "Workshop zu Django",
                "requirements": "Beamer und Tische",
            },
        )

        self.assertRedirects(response, reverse("base:index"))
        contribution = Contribution.objects.get()
        self.assertEqual(contribution.fk_event, self.event)
        self.assertEqual(contribution.fk_contributor, self.contributor)
        self.assertEqual(contribution.status, Contribution.Status.PENDING)


class GetContributionsForEventTests(ContributionTestMixin, TestCase):
    def test_only_contributions_for_selected_event_are_returned(self):
        selected = self.create_contribution(self.event)
        self.create_contribution(self.other_event)

        result = get_contributions_for_event(self.event.pk)

        self.assertEqual(list(result), [selected])

    def test_unknown_event_has_no_contributions(self):
        self.assertFalse(get_contributions_for_event(99999).exists())


class EventContributionsViewTests(ContributionTestMixin, TestCase):
    def setUp(self):
        self.client.force_login(self.organizer)

    def overview_url(self, event=None):
        if event is None:
            return reverse("contribution_overview")
        return reverse("event_contribution_list", args=[event.pk])

    def test_overview_url_selects_first_owned_event(self):
        response = self.client.get(self.overview_url())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["event"], self.event)
        self.assertQuerySetEqual(
            response.context["events"],
            [self.event, self.other_event],
        )
        self.assertNotContains(response, self.foreign_event.title)

    def test_organizer_can_switch_between_owned_events(self):
        response = self.client.get(self.overview_url(self.other_event))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["event"], self.other_event)
        self.assertContains(response, self.other_event.title)

    def test_legacy_event_url_remains_available(self):
        response = self.client.get(
            reverse("legacy_event_contribution_list", args=[self.event.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["event"], self.event)

    def test_only_selected_event_contributions_are_displayed(self):
        selected = self.create_contribution(
            self.event,
            description="Sichtbare Bewerbung",
        )
        self.create_contribution(
            self.other_event,
            description="Andere Bewerbung",
        )

        response = self.client.get(self.overview_url(self.event))

        self.assertQuerySetEqual(response.context["contributions"], [selected])
        self.assertContains(response, "Sichtbare Bewerbung")
        self.assertNotContains(response, "Andere Bewerbung")
        self.assertContains(response, "Offen")

    def test_foreign_event_returns_not_found(self):
        response = self.client.get(self.overview_url(self.foreign_event))

        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()

        response = self.client.get(self.overview_url())

        self.assertRedirects(response, reverse("base:login"))

    def test_contributor_is_redirected_to_index(self):
        self.client.force_login(self.contributor)

        response = self.client.get(self.overview_url())

        self.assertRedirects(response, reverse("base:index"))

    def test_user_without_organizer_permission_is_redirected_to_index(self):
        user = User.objects.create_user(username="plain-user", password="test12345")
        self.client.force_login(user)

        response = self.client.get(self.overview_url())

        self.assertRedirects(response, reverse("base:index"))

    def test_event_without_contributions_displays_empty_message(self):
        response = self.client.get(self.overview_url(self.event))

        self.assertContains(
            response,
            "Für diese Veranstaltung liegen noch keine Bewerbungen vor.",
        )

    def test_organizer_without_events_displays_empty_message(self):
        organizer = CustomUserOrganizer.objects.create_user(
            username="organizer-without-events",
            password="test12345",
            address=self.address,
            telephone="0341123458",
        )
        self.client.force_login(organizer)

        response = self.client.get(self.overview_url())

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["event"])
        self.assertContains(response, "Du hast noch keine eigenen Veranstaltungen.")

    def test_navigation_links_to_overview(self):
        response = self.client.get(self.overview_url())

        self.assertContains(response, f'href="{self.overview_url()}"')
