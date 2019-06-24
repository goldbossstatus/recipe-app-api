from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        '''
        test creating a new user with an email successul
        '''
        email = 'test@america.com'
        password = 'password'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        '''
        Test the email for a new user is normalized
        '''
        email = 'test@AMERICA.COM'
        user = get_user_model().objects.create_user(email, 'password')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        '''
        Test creating a user with no email will raise an error
        '''
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'password')

    def test_create_new_superuser(self):
        '''
        Test crating a new superuser
        '''
        user = get_user_model().objects.create_superuser(
            'test@america.com',
            'password'
        )
        # is_superuser is included as a part of the permissions mixin
        self.assertTrue(user.is_superuser)
        # we defined is_staff in models class User
        self.assertTrue(user.is_staff)
