from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


# Validator for telephone numbers.
telefon_validator = RegexValidator(
    regex=r"^\+?[0-9]{9,15}$",
    message="Bitte gib eine gültige Telefonnummer mit 9 bis 15 Ziffern ein.",
)


class Adress(models.Model):
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


class CustomUserOrganizer(models.Model):
    """
    Represent a user with the organizer role.

    Each user can have at most one organizer profile.
    Each address can be assigned to multiple organizer.

    Attributes:
        user (User): Zugehöriger Django-Benutzer.
        adress (Adress): Adresse des Organizers.
        telefone (str): Telefonnummer des Organizers.
        fax (str | None): Optionale Faxnummer des Organizers.
    """

    # Connect the organizer profile to a Django user.
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Connect the organizer to an address.
    # One address can belong to multiple organizers
    adress = models.ForeignKey(Adress, on_delete=models.PROTECT)

    # Store the organizer's telephone number.
    telephone = models.CharField(max_length=15,validators=[telefon_validator],)

    # Store an optional fax number.
    fax = models.CharField(max_length=15,validators=[telefon_validator],blank=True,null=True,)

    def __str__(self) -> str:
        """
        Return a readable representation of the organizer.

        Returns:
            str: Benutzer, Adresse, Telefonnummer und Faxnummer.
        """
        return f"{self.user}"


class CustomUserContributer(models.Model):
    """
    Represent a user with the contributor role.

    Each user can have at most one contributor profile.
    Multiple contributors can share the same address.

    Attributes:
        user (User): Zugehöriger Django-Benutzer.
        adress (Adress): Adresse des Contributors.
        telefone (str): Telefonnummer des Contributors.
        fax (str | None): Optionale Faxnummer des Contributors.
    """

    # Connect the contributor profile to a Django user.
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Connect the contributor to an address.
    # Multiple contributors can reference the same address.
    adress = models.ForeignKey(Adress, on_delete=models.PROTECT)

    # Store the contributor's telephone number.
    telephone = models.CharField(max_length=15,validators=[telefon_validator],)

    # Store an optional fax number.
    fax = models.CharField(max_length=15,validators=[telefon_validator],blank=True,null=True,)

    def __str__(self) -> str:
        """
        Return a readable representation of the contributor.

        Returns:
            str: Benutzer, Adresse, Telefonnummer und Faxnummer.
        """
        return f"{self.user}"
