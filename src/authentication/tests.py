from django.test import TestCase
from django.contrib.auth.models import User
from .models import CustomUserContributer, CustomUserOrganizer, Adress


class OrganizerCreationTest(TestCase):
    def test_Organizer_Creation(self):
        user = User.objects.create_user(
            username="FirmaNummer1",
            email="test@example.com",
            password="password123",
        )

        adress=Adress.objects.create(
            country="DE",
            city="Berlin",
            street="Teststraße",
            houseNbr=1,
        )

        organizer=CustomUserOrganizer.objects.create(
             user=user,
             adress=adress,
            telephone="+491234567890",
        )

        self.assertEqual(CustomUserOrganizer.objects.count(), 1)
        self.assertEqual(organizer.user.username, "FirmaNummer1")
        self.assertEqual(organizer.adress.city, "Berlin")

class ContributerCreationTest(TestCase):
        def test_Contributer_Creation(self):
            user = User.objects.create_user(
                username="Künstler1",
                first_name = "All",
                last_name="gemein",
                email="test@example.com",
                password="password123",
            )

            adress = Adress.objects.create(
                country="DE",
                city="Berlin",
                street="Teststraße",
                houseNbr=2,

            )

            contributer=CustomUserContributer.objects.create(
                user=user,
                adress=adress,
                telephone="+491234567890",
            )

            self.assertEqual(CustomUserContributer.objects.count(), 1)
            self.assertEqual(contributer.user.username, "Künstler1")
            self.assertEqual(contributer.adress.city, "Berlin")

class ContributerSameAsressCreationTest(TestCase):
        def test_Contributer_Creation(self):
            user = User.objects.create_user(
                username="Künstler1",
                first_name = "All",
                last_name="gemein",
                email="test@example.com",                        
                password="password123",
            )
                
        
            adress = Adress.objects.create(
                country="DE",
                city="Berlin",
                street="Teststraße",
                houseNbr=2,
            )
        
            contributer=CustomUserContributer.objects.create(
                user=user,
                adress=adress,
                telephone="+491234567890",
            )
        
            self.assertEqual(CustomUserContributer.objects.count(), 1)
            self.assertEqual(contributer.user.username, "Künstler1")
            self.assertEqual(contributer.adress.city, "Berlin")

            user2 = User.objects.create_user(
                username="Künstler2",
                first_name = "All",
                last_name="gemein2",
                email="test@example2.com",
                password="password123",
            )

            contributer2 = CustomUserContributer.objects.create(
                user=user2,
                adress=adress,
                telephone="+491234567890",
            )

            self.assertEqual(CustomUserContributer.objects.count(), 2)
            self.assertEqual(contributer2.user.username, "Künstler2")
            self.assertEqual(contributer2.adress.city, "Berlin")

            self.assertEqual(contributer.adress.pk, contributer2.adress.pk)

class PasswordCheckTest(TestCase):
     def test_password_check(self):
          user = User.objects.create_user(
                username="Künstler3",
                email="test@example3.com",
                password="password123",
          )

          self.assertNotEqual(user.password, "password123")
          self.assertTrue(user.check_password("password123"))
          self.assertFalse(user.check_password("wrongpass"))

