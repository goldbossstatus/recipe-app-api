from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import test, status
from rest_framework.test import APIClient
from core.models import Recipe
from recipe.serializers import RecipeSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def sample_recipe(user, **params):
    '''
    Create and return a sample recipe
    '''
    # set of default values with required recipe fields
    # any parameters that are passed in after 'user', will override any of
    # of the default values we set here.
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 10.00,
    }
    # update function from python library will allow us to customize
    defaults.update(params)
    # **defaults will convert our dictionary into an argument
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    '''
    Test unauthenticated user no recipe API access
    '''

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        '''
        test that login is required to access the endpoint
        '''
        # make unauthenticated request
        response = self.client.get(RECIPES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    '''
    Test authenticated Recipe API Access
    '''

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@america.com',
            password='testpassword',
            name='Test Name'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        '''
        test retrieving a list of recipes
        '''
        # create two recipe objects using our sample_recipe helper function.
        # do not need to assign them to a variable becuase we dont need to
        # access them in this test
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        # simulate get request
        response = self.client.get(RECIPES_URL)
        # now retrieve recipes from db
        recipes = Recipe.objects.all().order_by('-id')
        # pass our recipe into a serializer, return as a list(many=true)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert that the data equals the serializer that we created
        self.assertEqual(response.data, serializer.data)

    def test_recipes_limited_to_user(self):
        '''
        Test retrieving recipes to authenticated user
        '''
        user2 = create_user(
            email='test@user2.com',
            password='testpassword',
            name='Test Name'
        )
        # create a recipe object for each user, first unauthenticate user
        sample_recipe(user=user2)
        # second make recipe object for authenticated user
        sample_recipe(user=self.user)
        # simulate get http
        response = self.client.get(RECIPES_URL)
        # now filter recipes by authenticated user
        recipes = Recipe.objects.filter(user=self.user)
        # pass in returned queryset to serializer
        serializer = RecipeSerializer(recipes, many=True)
        # make assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)
