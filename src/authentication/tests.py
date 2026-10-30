from django.test import TestCase
from django.contrib.auth.models import User
from .models import CustomUserContributer, CustomUserOrganizer, Adress


# Tests the creation of an organizer and its relationship with a user and an address.
class OrganizerCreationTest(TestCase):
    # Checks whether an organizer is successfully created and saved with the correct data.
    def test_Organizer_Creation(self):
        user = User.objects.create_user(
            username="FirmaNummer1",
            email="test@example.com",
            password="password123",
        )

        # Creates an address that is assigned to the organizer.
        adress=Adress.objects.create(
            country="DE",
            city="Berlin",
            street="Teststraße",
            houseNbr=1,
        )

        # Creates an organizer and links it to the user and the address.
        organizer=CustomUserOrganizer.objects.create(
             user=user,
             adress=adress,
            telephone="+491234567890",
        )

        # Checks whether exactly one organizer was created.
        self.assertEqual(CustomUserOrganizer.objects.count(), 1)

        # Checks whether the organizer is linked to the correct user.
        self.assertEqual(organizer.user.username, "FirmaNummer1")

        # Checks whether the organizer's address was saved correctly.
        self.assertEqual(organizer.adress.city, "Berlin")


# Tests the creation of a contributor and its relationship with a user and an address.
class ContributerCreationTest(TestCase):
        # Checks whether a contributor is successfully created and saved with the correct data.
        def test_Contributer_Creation(self):
            user = User.objects.create_user(
                username="Künstler1",
                first_name = "All",
                last_name="gemein",
                email="test@example.com",
                password="password123",
            )

            # Creates an address that is assigned to the contributor.
            adress = Adress.objects.create(
                country="DE",
                city="Berlin",
                street="Teststraße",
                houseNbr=2,

            )

            # Creates a contributor and links it to the user and the address.
            contributer=CustomUserContributer.objects.create(
                user=user,
                adress=adress,
                telephone="+491234567890",
            )

            # Checks whether exactly one contributor was created.
            self.assertEqual(CustomUserContributer.objects.count(), 1)

            # Checks whether the contributor is linked to the correct user.
            self.assertEqual(contributer.user.username, "Künstler1")

            # Checks whether the contributor's address was saved correctly.
            self.assertEqual(contributer.adress.city, "Berlin")


# Tests whether multiple contributors can use the same address.
class ContributerSameAsressCreationTest(TestCase):
        # Checks whether two contributors can be created successfully using the same address.
        def test_Contributer_Creation(self):
            user = User.objects.create_user(
                username="Künstler1",
                first_name = "All",
                last_name="gemein",
                email="test@example.com",                        
                password="password123",
            )
                
        
            # Creates an address that will be used by both contributors.
            adress = Adress.objects.create(
                country="DE",
                city="Berlin",
                street="Teststraße",
                houseNbr=2,
            )
        
            # Creates the first contributor and links it to the address.
            contributer=CustomUserContributer.objects.create(
                user=user,
                adress=adress,
                telephone="+491234567890",
            )
        
            # Checks whether the first contributor was created successfully.
            self.assertEqual(CustomUserContributer.objects.count(), 1)

            # Checks whether the first contributor is linked to the correct user.
            self.assertEqual(contributer.user.username, "Künstler1")

            # Checks whether the first contributor's address was saved correctly.
            self.assertEqual(contributer.adress.city, "Berlin")

            user2 = User.objects.create_user(
                username="Künstler2",
                first_name = "All",
                last_name="gemein2",
                email="test@example2.com",
                password="password123",
            )

            # Creates the second contributor and assigns the same address to it.
            contributer2 = CustomUserContributer.objects.create(
                user=user2,
                adress=adress,
                telephone="+491234567890",
            )

            # Checks whether both contributors were saved in the database.
            self.assertEqual(CustomUserContributer.objects.count(), 2)

            # Checks whether the second contributor is linked to the correct user.
            self.assertEqual(contributer2.user.username, "Künstler2")

            # Checks whether the second contributor's address was saved correctly.
            self.assertEqual(contributer2.adress.city, "Berlin")

            # Checks whether both contributors reference the same address.
            self.assertEqual(contributer.adress.pk, contributer2.adress.pk)


# Tests whether Django hashes passwords correctly and verifies them as expected.
class PasswordCheckTest(TestCase):
     # Checks whether the password is stored as a hash and can be verified correctly.
     def test_password_check(self):
          user = User.objects.create_user(
                username="Künstler3",
                email="test@example3.com",
                password="password123",
          )

          # Checks whether the stored password is not in plain text.
          self.assertNotEqual(user.password, "password123")

          # Checks whether the correct password is accepted.
          self.assertTrue(user.check_password("password123"))

          # Checks whether an incorrect password is rejected.
          self.assertFalse(user.check_password("wrongpass"))