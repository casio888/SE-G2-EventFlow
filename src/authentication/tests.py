from django.test import TestCase

from .models import User


class UserPasswordTest(TestCase):
    def test_check_password_with_hashed_password(self):
        user = User(
            email="test@example.com",
            password="password123",
            firmenname="Test GmbH",
            firmensitzLand="DE",
            firmensitzOrt="Berlin",
            firmensitzStraße="Teststraße",
            firmensitzHausnummer=1,
            telefon="+491234567890",
        )
        user.save()

        self.assertNotEqual(user.password, "password123")
        self.assertTrue(user.check_password("password123"))
        self.assertFalse(user.check_password("wrongpass"))
