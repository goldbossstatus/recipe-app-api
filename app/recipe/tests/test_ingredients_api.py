from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, Recipe
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

    def test_create_ingredients_successful(self):
        '''
        Test create a new Ingredient
        '''
        payload = {'name': 'Romain Lettuce'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        '''
        Test creating invalid ingredient payload fails
        '''
        payload = {
            'name': '',
        }
        response = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        '''
        Test filtering ingredients by those assigned to recipes
        '''
        # create two ingredients, leave ingredient2 unassigned
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Peach'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='Butter'
        )
        # create a recipe
        recipe1 = Recipe.objects.create(
            title='Peach Cobbler',
            time_minutes=15,
            price=7,
            user=self.user,
        )
        # assign ingredient1 to the recipe1
        recipe1.ingredients.add(ingredient1)
        # make hhtp call
        response = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        # serialize ingredients
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        # make sure we get back only ingredient assigned to recipe
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_retrieve_ingredients_assigned_unique(self):
        '''
        Test filtering ingredients by assigned returns unique items
        '''
        # create an ingredient that will be assigned
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Tea'
        )
        # create ingredient object that will not get assigned
        Ingredient.objects.create(
            user=self.user,
            name='Elevensies'
        )
        # create a recipe
        recipe1 = Recipe.objects.create(
            title='Afternoon Tea',
            time_minutes=5,
            price=2,
            user=self.user,
        )
        # assign ingredient1 to recipe 1
        recipe1.ingredients.add(ingredient1)
        # create a second recipe
        recipe2 = Recipe.objects.create(
            title='Luncheon',
            time_minutes=30,
            price=15,
            user=self.user,
        )
        # assign ingredient1 to recipe 2
        recipe2.ingredients.add(ingredient1)
        # make http call
        response = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        # make sure we only get 1 ingredient object returned
        self.assertEqual(len(response.data), 1)
