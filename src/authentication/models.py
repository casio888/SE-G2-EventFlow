from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


# Validator for telephone numbers.
telefon_validator = RegexValidator(
    regex=r"^\+?[0-9]{9,15}$",
    message="Bitte gib eine gültige Telefonnummer mit 9 bis 15 Ziffern ein.",
)


class Address(models.Model):
    """
    Represent an address.

    Addresses are stored in a separate model so that the same address
    can be referenced by multiple user profiles.

    Attributes:
        country (str): Land der Adresse.
        city (str): Stadt der Adresse.
        street (str): Straße der Adresse.
        houseNbr (int): Hausnummer der Adresse.
    """

    country = models.CharField(max_length=50)
    city = models.CharField(max_length=170)
    street = models.CharField(max_length=85)
    houseNbr = models.IntegerField()

    def __str__(self) -> str:
        """
        Return the address as a readable string.

        Returns:
            str: Lan    d, Stadt, Straße und Hausnummer.
        """
        return f"{self.country}, {self.city}, {self.street}, {self.houseNbr}"


class CustomUserOrganizer(User):

    """
    Represents an organizer account in the system.

    Extends Django's built-in User model with additional contact
    information and an associated address.

    Attributes:
        address (Address): Address associated with the organizer.
        telephone (str): Telephone number of the organizer.
        fax (str | None): Optional fax number of the organizer.
    """

    # Connect the organizer to an address.
    # One address can belong to multiple organizers.
    address = models.ForeignKey(Address, on_delete=models.PROTECT)

    # Store the organizer's telephone number.
    telephone = models.CharField(max_length=15,validators=[telefon_validator],)

    # Store an optional fax number.
    fax = models.CharField(max_length=15,validators=[telefon_validator],blank=True,null=True,)

    class Meta:
        verbose_name = "Organizer"
        verbose_name_plural = "Organizers"

    def __str__(self) -> str:
        """
        Return a readable representation of the organizer.

        Returns:
            str: Username of the organizer.
        """
        
        return f"{self.username}"


class CustomUserContributer(User):

    """
    Represents a contributor account in the system.

    Extends Django's built-in User model with additional contact
    information and an associated address.

    Attributes:
        address (Address): Address associated with the contributor.
        telephone (str): Telephone number of the contributor.
        fax (str | None): Optional fax number of the contributor.
    """

    # Connect the contributor to an address.
    # One address can belong to multiple contributors.
    address = models.ForeignKey(Address, on_delete=models.PROTECT)

    # Store the contributor's telephone number.
    telephone = models.CharField(max_length=15,validators=[telefon_validator],)

    # Store an optional fax number.
    fax = models.CharField(max_length=15,validators=[telefon_validator],blank=True,null=True,)
    class Meta:
        verbose_name = "Contributor"
        verbose_name_plural = "Contributors"

    def __str__(self) -> str:
        """
        Return a readable representation of the contributor.

        Returns:
            str: Username of the contributor.
        """
        
        return f"{self.username}"
    