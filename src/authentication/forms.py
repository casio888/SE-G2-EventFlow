from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUserContributer, CustomUserOrganizer, Adress, telefon_validator


class UserOrganizerRegestrationForm(UserCreationForm):
    """Form for registering an organizer representing a company or association."""

    # Validate the telephone number using the shared telephone validator.
    telephone = forms.CharField(max_length=15, validators=[telefon_validator],)

    # Collect an optional fax number and validate it if provided.
    fax = forms.CharField(max_length=15, validators=[telefon_validator],required=False,)

    # Collect the address details of the organization.
    country = forms.CharField(max_length=50)
    city = forms.CharField(max_length=170)
    street = forms.CharField(max_length=85)
    houseNbr = forms.IntegerField()

    class Meta:
        """Define the Django user model and the fields included in the form."""

        model = User
        fields = [
            "username",
            "email",
            "telephone",
            "fax",
            "country",
            "city",
            "street",
            "houseNbr",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        """Save the user, address, and organizer profile.

        Args:
            commit (bool): Whether to save the user and related objects
                to the database.

        Returns:
            User: The created or prepared Django user.
        """

        # Prepare the user object without immediately saving it to the database.
        user = super().save(commit=False)

        if commit:
            # Save the user before creating objects that reference it.
            user.save()

            # Create a separate address record for the organization.
            adress, _ = Adress.objects.get_or_create(
                country=self.cleaned_data["country"],
                city=self.cleaned_data["city"],
                street=self.cleaned_data["street"],
                houseNbr=self.cleaned_data["houseNbr"],
            )

            # Link the user and address to the organizer profile.
            CustomUserOrganizer.objects.create(
                user=user,
                adress=adress,
                telephone=self.cleaned_data["telephone"],
                fax=self.cleaned_data["fax"]
            )

        # Return the user, whether saved or not.
        return user


class UserContributerRegestrationForm(UserCreationForm):
    """Form for registering a contributor with contact and address details."""

    # Validate the telephone number using the shared telephone validator.
    telephone = forms.CharField(max_length=15, validators=[telefon_validator],)

    # Collect an optional fax number and validate it if provided.
    fax = forms.CharField(max_length=15, validators=[telefon_validator],required=False,)

    # Collect the contributor's address details.
    country = forms.CharField(max_length=50)
    city = forms.CharField(max_length=170)
    street = forms.CharField(max_length=85)
    houseNbr = forms.IntegerField()

    class Meta:
        """Define the Django user model and the fields included in the form."""

        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "telephone",
            "fax",
            "country",
            "city",
            "street",
            "houseNbr",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        """Save the user, address, and contributor profile.

        Args:
            commit (bool): Whether to save the user and related objects
                to the database.

        Returns:
            User: The created or prepared Django user.
        """

        # Prepare the user object without immediately saving it to the database.
        user = super().save(commit=False)

        if commit:
            # Save the user before creating objects that reference it.
            user.save()

            # Create a separate address record for the contributor.
            adress, _ = Adress.objects.get_or_create(
                country=self.cleaned_data["country"],
                city=self.cleaned_data["city"],
                street=self.cleaned_data["street"],
                houseNbr=self.cleaned_data["houseNbr"],
            )

            # Link the user and address to the contributor profile.
            CustomUserContributer.objects.create(
                user=user,
                adress=adress,
                telephone=self.cleaned_data["telephone"],
                fax=self.cleaned_data["fax"]
            )

        # Return the user, whether saved or not.
        return user