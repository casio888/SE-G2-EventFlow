from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import check_password, identify_hasher, make_password

telefon_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Die Telefonnummer muss im Format '+999999999' sein und zwischen 9 und 15 Ziffern enthalten." #minh wenn du das nicht formatiert bekommst lösch das einfach
)

class User(models.Model):
    email=models.EmailField(max_length=160, unique=True)
    password=models.CharField(max_length = 100)

    firmenname=models.CharField(max_length=200)

    firmensitzLand=models.CharField(max_length=50)
    firmensitzOrt=models.CharField(max_length=170)
    firmensitzStraße=models.CharField(max_length=85)
    firmensitzHausnummer=models.IntegerField()

    telefon=models.CharField(max_length = 15, validators=[telefon_validator])
    fax=models.CharField(max_length = 15, validators=[telefon_validator], blank=True, null=True)

    angemeldet = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email
