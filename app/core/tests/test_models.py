from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@america.com', password='testpassword'):
    '''
    Create a sample user
    '''
    return get_user_model().objects.create_user(email, password)


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

    def test_tag_str(self):
        '''
        Test the tag string representation
        '''
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan',
        )
        # we create a tag and then convert our tag model into a string, it
        # gives us the name
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        '''
        Test the ingredient string representation
        '''
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Jalapeno',
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        '''
        Test the recipe string representation
        '''
        # create sample recipe
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Beef Wellington',
            time_minutes=5,
            price=15.00
        )
        self.assertEqual(str(recipe), recipe.title)
