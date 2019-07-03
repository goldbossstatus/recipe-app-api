from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicIngredientsApiTests(TestCase):
    '''
    Test the publicly available ingredients API
    '''

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        '''
        Test that login is required to access the endpoint
        '''
        response = self.client.get(INGREDIENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    '''
    Test the private ingredients API
    '''

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@america.com',
            password='testpassword',
            name='Test Name'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        '''
        Test retrieving a list of ingedients
        '''
        # sample ingredients
        Ingredient.objects.create(user=self.user, name='salt')
        Ingredient.objects.create(user=self.user, name='garlic')

        response = self.client.get(INGREDIENTS_URL)
        # verify that returned result matches serialized ingredients
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_user(self):
        '''
        Test that ingredients are returned for auth'd user
        '''
        payload = {
            'email': 'test@user2.com',
            'password': 'password',
            'name': 'Test Name'
        }
        user2 = create_user(**payload)
        Ingredient.objects.create(user=user2, name='pepper')
        ingredient = Ingredient.objects.create(user=self.user, name='rosemary')

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn(response.data[0]['name'], ingredient.name)
