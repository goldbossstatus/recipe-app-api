from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        '''
        test creating a new user with an email successfully
        '''
        # we are going to pass in an email address and a password as the
        # arguments and verify that a user was created, and an
        # email was correct as well as the password
        email = 'test@america.com'
        password = 'password'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        # run assertions to make sure users were crated successfully
        self.assertEqual(user.email, email)
        # password is encrypted so must use different boolean to test
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
        # we add None to the test, so that when we run the program, it should
        # raise a value error, and if it doesn't raise a value error, the test
        # will fail
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
