from django import forms
from django.contrib.auth.models import User,Group
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import CustomUserContributer, CustomUserOrganizer, Address, telephone_validator


class UserOrganizerRegestrationForm(UserCreationForm):

    """
    Form for registering a new organizer account.

    Extends Django's UserCreationForm with additional contact information
    and address fields. Creates or retrieves an address record and
    associates it with the organizer account.

    Arguments:
        commit (bool): Determines whether the user instance is saved
            to the database.

    Returns:
        CustomUserOrganizer: The created organizer instance.
    """

    # Validate the telephone number using the shared telephone validator.
    telephone = forms.CharField(max_length=15, validators=[telephone_validator],)

    # Collect an optional fax number and validate it if provided.
    fax = forms.CharField(max_length=15, validators=[telephone_validator],required=False,)

    # Collect the address details of the organization.
    country = forms.CharField(max_length=50)
    city = forms.CharField(max_length=170)
    street = forms.CharField(max_length=85)
    houseNbr = forms.IntegerField()

    class Meta:
        model = CustomUserOrganizer

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

    @transaction.atomic
    def save(self, commit=True):
    
        """
        Save the organizer registration form.

        Creates an organizer instance without immediately saving it,
        assigns the telephone and fax numbers, and creates or retrieves
        the associated address.

        Arguments:
            commit (bool): Determines whether the organizer instance
                is saved to the database.

        Returns:
            CustomUserOrganizer: The organizer instance.
        """
        user = super().save(commit=False)

        user.telephone=self.cleaned_data["telephone"]
        user.fax=self.cleaned_data["fax"]

        # Create a separate address record for the organizer.
        user.address, _ = Address.objects.get_or_create(
            country=self.cleaned_data["country"],
            city=self.cleaned_data["city"],
            street=self.cleaned_data["street"],
            houseNbr=self.cleaned_data["houseNbr"],
        )

        if commit:
            user.save()

        return user

class UserContributerRegestrationForm(UserCreationForm):

    """
    Form for registering a new contributor account.

    Extends Django's UserCreationForm with additional contact information
    and address fields. Creates or retrieves an address record and
    associates it with the contributor account.

    Arguments:
        commit (bool): Determines whether the user instance is saved
            to the database.

    Returns:
        CustomUserContributer: The created contributor instance.
    """

    # Validate the telephone number using the shared telephone validator.
    telephone = forms.CharField(max_length=15, validators=[telephone_validator],)

    # Collect an optional fax number and validate it if provided.
    fax = forms.CharField(max_length=15, validators=[telephone_validator],required=False,)

    # Collect the address details of the organization.
    country = forms.CharField(max_length=50)
    city = forms.CharField(max_length=170)
    street = forms.CharField(max_length=85)
    houseNbr = forms.IntegerField()

    class Meta:
        model = CustomUserContributer

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

    @transaction.atomic
    def save(self, commit=True):
        """
        Save the contributor registration form.

        Creates a contributor instance without immediately saving it,
        assigns the telephone and fax numbers, and creates or retrieves
        the associated address.

        Arguments:
            commit (bool): Determines whether the contributor instance
                is saved to the database.

        Returns:
            CustomUserContributer: The contributor instance.
        """
        user = super().save(commit=False)

        user.telephone=self.cleaned_data["telephone"]
        user.fax=self.cleaned_data["fax"]

        user.address, _ = Address.objects.get_or_create(
            country=self.cleaned_data["country"],
            city=self.cleaned_data["city"],
            street=self.cleaned_data["street"],
            houseNbr=self.cleaned_data["houseNbr"],
        )

        if commit:
            user.save()

        return user