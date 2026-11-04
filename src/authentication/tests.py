from django.contrib.auth.models import User
from django.db.models import ProtectedError
from django.test import TestCase

from .forms import UserContributerRegestrationForm,UserOrganizerRegestrationForm

from .models import Address, CustomUserContributer, CustomUserOrganizer

from django.contrib.auth.hashers import check_password  

def valid_data(**overrides):
    """Return valid registration data.

    Builds a fresh dictionary with valid values for all registration
    form fields. Individual fields can be replaced via keyword
    arguments, so a test only has to state what differs from the
    valid default.

    Arguments:
        overrides {dict} -- Field names and values that replace the defaults

    Returns:
        dict -- Valid form data with the given overrides applied
    """
    data = {
        "username": "user1",
        "email": "user1@example.com",
        "telephone": "+491701234567",
        "fax": "",
        "country": "Deutschland",
        "city": "Dresden",
        "street": "Teststraße",
        "houseNbr": 12,
        "password1": "SuperSicheresPasswort123!",
        "password2": "SuperSicheresPasswort123!",
    }
    data.update(overrides)
    return data


class UserRegistrationTests(TestCase):
    """Test the successful registration of organizers and contributors.

    Covers the positive case: a valid form creates the user, stores the
    contact data, hashes the password and links an address.
    """

    def test_organizer_registration_creates_user(self):
        """Test that a valid form creates an organizer.

        Checks that the organizer exists in the database, that contact
        data and address are stored correctly and that the password is
        hashed instead of stored in plain text.
        """
        data = valid_data(username="organizer1", email="organizer1@example.com")

        form = UserOrganizerRegestrationForm(data)
        self.assertTrue(form.is_valid(), form.errors)

        user = form.save()

        # The organizer was created in the database.
        self.assertEqual(CustomUserOrganizer.objects.count(), 1)
        organizer = CustomUserOrganizer.objects.get(username="organizer1")
        self.assertEqual(organizer.pk, user.pk)

        # Contact data was stored correctly.
        self.assertEqual(organizer.email, "organizer1@example.com")
        self.assertEqual(organizer.telephone, "+491701234567")

        # The password was hashed and not stored in plain text.
        self.assertNotEqual(organizer.password, data["password1"])
        self.assertTrue(check_password(data["password1"], organizer.password))

        # The address was created and linked to the organizer.
        self.assertEqual(Address.objects.count(), 1)
        self.assertEqual(organizer.address.city, "Dresden")
        self.assertEqual(organizer.address.houseNbr, 12)

    def test_contributor_registration_creates_user(self):
        """Test that a valid form creates a contributor.

        Checks that the contributor exists in the database, that
        personal data, contact data (including the optional fax number)
        and address are stored correctly and that the password is hashed.
        """
        data = valid_data(
            username="contributor1",
            first_name="Max",
            last_name="Mustermann",
            email="contributor1@example.com",
            fax="+493511234567",
        )

        form = UserContributerRegestrationForm(data)
        self.assertTrue(form.is_valid(), form.errors)

        user = form.save()

        # The contributor was created in the database.
        self.assertEqual(CustomUserContributer.objects.count(), 1)
        contributor = CustomUserContributer.objects.get(username="contributor1")
        self.assertEqual(contributor.pk, user.pk)

        # Personal and contact data was stored correctly.
        self.assertEqual(contributor.first_name, "Max")
        self.assertEqual(contributor.last_name, "Mustermann")
        self.assertEqual(contributor.email, "contributor1@example.com")
        self.assertEqual(contributor.telephone, "+491701234567")
        self.assertEqual(contributor.fax, "+493511234567")

        # The password was hashed.
        self.assertTrue(check_password(data["password1"], contributor.password))

        # The address was created and linked to the contributor.
        self.assertEqual(Address.objects.count(), 1)
        self.assertEqual(contributor.address.street, "Teststraße")


class OrganizerRegistrationErrorTests(TestCase):
    """Test invalid input for the organizer registration form.

    Covers the negative cases: invalid phone and fax numbers, mismatching
    passwords, duplicate usernames, missing fields and wrong data types.
    """

    def assertInvalidField(self, field, **overrides):
        """Assert that the form is invalid because of a specific field.

        Builds the organizer form from valid data with the given
        overrides and checks that validation fails and reports an error
        on the expected field.

        Arguments:
            field {str} -- Name of the field that must contain an error
            overrides {dict} -- Field values that replace the valid defaults

        Raises:
            AssertionError -- If the form is valid or has no error on the field
        """
        form = UserOrganizerRegestrationForm(valid_data(**overrides))
        self.assertFalse(form.is_valid())
        self.assertIn(field, form.errors)

    def test_invalid_telephone_numbers(self):
        """Test that invalid telephone numbers are rejected.

        Runs one sub-test per invalid number (too short, letters,
        spaces, too long) and expects an error on the telephone field.
        """
        invalid_numbers = [
            "12345",              # too short
            "abc123456789",       # contains letters
            "+49 170 1234567",    # contains spaces
            "+4917012345678901",  # too long
        ]
        for number in invalid_numbers:
            with self.subTest(telephone=number):
                self.assertInvalidField("telephone", telephone=number)

    def test_invalid_fax_number(self):
        """Test that an invalid fax number is rejected.

        A fax number containing letters must produce an error on the
        fax field.
        """
        self.assertInvalidField("fax", fax="abc")

    def test_fax_is_optional(self):
        """Test that the fax number may be left empty.

        A form without a fax number must be valid, and the saved
        organizer must store an empty string.
        """
        form = UserOrganizerRegestrationForm(valid_data(fax=""))
        self.assertTrue(form.is_valid(), form.errors)
        organizer = form.save()
        self.assertEqual(organizer.fax, "")

    def test_passwords_do_not_match(self):
        """Test that mismatching passwords are rejected.

        Different values in password1 and password2 must produce an
        error on password2.
        """
        self.assertInvalidField("password2", password2="AnderesPasswort456!")

    def test_duplicate_username(self):
        """Test that an already used username is rejected.

        Registers one organizer first, then expects an error on the
        username field when the same username is submitted again.
        """
        first = UserOrganizerRegestrationForm(valid_data())
        self.assertTrue(first.is_valid(), first.errors)
        first.save()

        self.assertInvalidField("username", email="other@example.com")

    def test_missing_required_fields(self):
        """Test that every required field must be filled.

        Runs one sub-test per required field. The field is removed from
        otherwise valid data and the form must report an error on it.
        """
        required = [
            "username", "telephone", "country", "city",
            "street", "houseNbr", "password1", "password2",
        ]
        for field in required:
            with self.subTest(field=field):
                data = valid_data()
                data.pop(field)
                form = UserOrganizerRegestrationForm(data)
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)

    def test_house_number_must_be_integer(self):
        """Test that the house number must be a number.

        A non-numeric value must produce an error on the houseNbr field.
        """
        self.assertInvalidField("houseNbr", houseNbr="zwölf")

    def test_invalid_form_creates_nothing(self):
        """Test that an invalid form writes nothing to the database.

        After a failed validation, neither an organizer nor an address
        may exist.
        """
        form = UserOrganizerRegestrationForm(valid_data(telephone="123"))
        self.assertFalse(form.is_valid())

        # Neither a user nor an address may exist after a failed validation.
        self.assertEqual(CustomUserOrganizer.objects.count(), 0)
        self.assertEqual(Address.objects.count(), 0)


class ContributorRegistrationErrorTests(TestCase):
    """Test invalid input for the contributor registration form.

    Covers the most important error cases of the contributor form and
    the username uniqueness across both roles.
    """

    def test_invalid_telephone(self):
        """Test that an invalid telephone number is rejected.

        A too short number must produce an error on the telephone field.
        """
        form = UserContributerRegestrationForm(
            valid_data(first_name="Max", last_name="Mustermann", telephone="12345")
        )
        self.assertFalse(form.is_valid())
        self.assertIn("telephone", form.errors)

    def test_passwords_do_not_match(self):
        """Test that mismatching passwords are rejected.

        Different values in password1 and password2 must produce an
        error on password2.
        """
        form = UserContributerRegestrationForm(
            valid_data(
                first_name="Max",
                last_name="Mustermann",
                password2="AnderesPasswort456!",
            )
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_username_is_unique_across_roles(self):
        """Test that usernames are unique across organizers and contributors.

        Both models inherit from User, so a username taken by an
        organizer must be rejected in the contributor form.
        """
        # Both roles inherit from User, so usernames share one namespace.
        organizer_form = UserOrganizerRegestrationForm(valid_data(username="shared"))
        self.assertTrue(organizer_form.is_valid(), organizer_form.errors)
        organizer_form.save()

        contributor_form = UserContributerRegestrationForm(
            valid_data(username="shared", first_name="Max", last_name="Mustermann")
        )
        self.assertFalse(contributor_form.is_valid())
        self.assertIn("username", contributor_form.errors)


class AddressReuseTests(TestCase):
    """Test the reuse of addresses during registration.

    The forms use get_or_create, so identical addresses must share one
    Address record while different addresses create new ones.
    """

    def test_same_address_is_reused_by_two_organizers(self):
        """Test that two organizers with the same address share one record.

        Registers two organizers with identical address data and expects
        a single Address record referenced by both.
        """
        for name in ("org1", "org2"):
            form = UserOrganizerRegestrationForm(
                valid_data(username=name, email=f"{name}@example.com")
            )
            self.assertTrue(form.is_valid(), form.errors)
            form.save()

        self.assertEqual(Address.objects.count(), 1)
        org1 = CustomUserOrganizer.objects.get(username="org1")
        org2 = CustomUserOrganizer.objects.get(username="org2")
        self.assertEqual(org1.address_id, org2.address_id)

    def test_same_address_is_shared_between_roles(self):
        """Test that an organizer and a contributor can share an address.

        Registers one user per role with identical address data and
        expects a single Address record.
        """
        organizer_form = UserOrganizerRegestrationForm(valid_data(username="org"))
        self.assertTrue(organizer_form.is_valid(), organizer_form.errors)
        organizer_form.save()

        contributor_form = UserContributerRegestrationForm(
            valid_data(username="con", first_name="Max", last_name="Mustermann")
        )
        self.assertTrue(contributor_form.is_valid(), contributor_form.errors)
        contributor_form.save()

        self.assertEqual(Address.objects.count(), 1)

    def test_different_address_creates_new_record(self):
        """Test that a different address creates a new record.

        Registers two organizers with different house numbers and
        expects two separate Address records.
        """
        for name, nbr in (("org1", 1), ("org2", 2)):
            form = UserOrganizerRegestrationForm(
                valid_data(username=name, houseNbr=nbr)
            )
            self.assertTrue(form.is_valid(), form.errors)
            form.save()

        self.assertEqual(Address.objects.count(), 2)


class AuthenticationModelTests(TestCase):
    """Test the basic behaviour of the authentication models.

    Covers string representations, the inheritance from User and the
    protection of addresses that are still in use.
    """

    def setUp(self):
        """Create the shared address used by all tests in this class.

        Django runs this method automatically before every test, so
        each test can access the address via self.address.
        """
        self.address = Address.objects.create(
            country="Deutschland",
            city="Dresden",
            street="Teststraße",
            houseNbr=12,
        )

    def test_address_str(self):
        """Test the string representation of an address.

        The result must contain country, city, street and house number
        separated by commas.
        """
        self.assertEqual(
            str(self.address), "Deutschland, Dresden, Teststraße, 12"
        )

    def test_organizer_str_returns_username(self):
        """Test the string representation of an organizer.

        The result must be the username of the organizer.
        """
        organizer = CustomUserOrganizer.objects.create_user(
            username="org1",
            password="SuperSicheresPasswort123!",
            telephone="+491701234567",
            address=self.address,
        )
        self.assertEqual(str(organizer), "org1")

    def test_contributor_str_returns_username(self):
        """Test the string representation of a contributor.

        The result must be the username of the contributor.
        """
        contributor = CustomUserContributer.objects.create_user(
            username="con1",
            password="SuperSicheresPasswort123!",
            telephone="+491701234567",
            address=self.address,
        )
        self.assertEqual(str(contributor), "con1")

    def test_organizer_is_also_a_django_user(self):
        """Test that an organizer also exists as a Django User.

        Because of multi-table inheritance, creating an organizer must
        also create a matching row in the auth_user table.
        """
        # Multi-table inheritance creates a matching row in auth_user.
        CustomUserOrganizer.objects.create_user(
            username="org1",
            password="SuperSicheresPasswort123!",
            telephone="+491701234567",
            address=self.address,
        )
        self.assertTrue(User.objects.filter(username="org1").exists())

    def test_address_in_use_cannot_be_deleted(self):
        """Test that an address referenced by a user cannot be deleted.

        The foreign key uses on_delete=PROTECT, so deleting the address
        must raise a ProtectedError.
        """
        CustomUserOrganizer.objects.create_user(
            username="org1",
            password="SuperSicheresPasswort123!",
            telephone="+491701234567",
            address=self.address,
        )
        # on_delete=PROTECT must block the deletion.
        with self.assertRaises(ProtectedError):
            self.address.delete()