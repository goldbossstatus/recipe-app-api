from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


# /api/recipe/recipes
RECIPES_URL = reverse('recipe:recipe-list')


# /api/recipe/recipes/2
def detail_recipe_url(recipe_id):
    '''
    Return recipe detail URL
    '''
    # you specify arguments with the reverse function by passing in args
    # and a list of the arguments you want to add.
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main Course'):
    '''
    Create and return a sample tag
    '''
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='chocolate'):
    '''
    Create and return a sample ingredient
    '''
    return Ingredient.objects.create(user=user, name=name)


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

    def test_view_recipe_detail(self):
        '''
        test viewing a recipe detail
        '''
        # create a sample recipe
        recipe = sample_recipe(user=self.user)
        # add a tag
        recipe.tags.add(sample_tag(user=self.user))
        # add an ingredient
        recipe.ingredients.add(sample_ingredient(user=self.user))
        # generate a url that we will call
        url = detail_recipe_url(recipe.id)
        # generate http get for the url
        response = self.client.get(url)
        # now we expect the response to be serialized
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(response.data, serializer.data)

    def test_create_basic_recipe(self):
        '''
        Test creating recipe for auth'd user
        '''
        # create payload with minimum required fields for creating new recipe
        payload = {
            'title': 'Lava Cake',
            'time_minutes': 25,
            'price': 7.00
        }
        # post the payload dictionary to RECIPES_URL
        response = self.client.post(RECIPES_URL, payload)
        # standard hjttp repsonse code for creating objects in an api
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # when you create an object using gjango rest framework, the default
        # behavior is it will return a dictionary containg the created object!
        # retrieve created recipe from our models
        recipe = Recipe.objects.get(id=response.data['id'])
        # loop through each keys and check that the correct value is assigned
        # to recipe model
        for key in payload.keys():
            # getattr is a python helper function that allows you to retrieve
            # an attribute from an object by passing in a variable.
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        '''
        Test creating recipe with tags
        '''
        # create 2 sample tags to test
        tag1 = sample_tag(user=self.user, name='Mexican')
        tag2 = sample_tag(user=self.user, name='Appetizer')
        # now create a recipe and assign the tags to the recipe
        payload = {
            'title': 'Avocado Dip',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 30,
            'price': 20.00,
        }
        # make http post request
        response = self.client.post(RECIPES_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # retrieve recipe that was created
        recipe = Recipe.objects.get(id=response.data['id'])
        # retieve tags that were created with the recipe
        # because we have a manytomany field assigned to our tags,
        # this will return all of the tags that were assigned to our recipe
        # as a queryset and store them in a tags variable.
        tags = recipe.tags.all()
        # assert that our TWO tags were returned
        self.assertEqual(tags.count(), 2)
        # now assert that tags we created as our sample tags are the same
        # that are in our query set.
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        '''
        Test creating recipe with ingredients
        '''
        # create sample ingredients
        ingredient1 = sample_ingredient(user=self.user, name='Avocado')
        ingredient2 = sample_ingredient(user=self.user, name='tomato')
        # now create a recipe and assign the ingredients to the recipe
        payload = {
            'title': 'Avocado Dip',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 30,
            'price': 20.00
        }
        # make http post request
        response = self.client.post(RECIPES_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # retrieve recipe that was created
        recipe = Recipe.objects.get(id=response.data['id'])
        # retrieve ingredients that were created with recipe
        ingredients = recipe.ingredients.all()
        # assert that our TWO ingredients were returned
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_updated_recipe(self):
        '''
        Test updating a recipe with patch
        '''
        # create sample recipe
        recipe = sample_recipe(user=self.user)
        # add a tag 1
        recipe.tags.add(sample_tag(user=self.user))
        # add a new tag we will replace tag 1 with
        new_tag = sample_tag(user=self.user, name='Dessert')
        # create payload with a different title to update old title
        payload = {
            'title': 'Fondant Tart',
            'tags': [new_tag.id]
        }
        # create a our recipe from our detail url
        url = detail_recipe_url(recipe.id)
        # make http patch request
        self.client.patch(url, payload)
        # retrieve and update to the recipe from the database
        # the details will not change in db unless you call refresh_from_db
        recipe.refresh_from_db()
        # assert that the title is equal to the new title, Fondant Tart
        self.assertEqual(recipe.title, payload['title'])
        # retrieve all of the tags that are assigned to this recipe
        tags = recipe.tags.all()
        # assert that the length of the tags is 1, because we only patched 1
        self.assertEqual(len(tags), 1)
        # assert that the new tag is in the tags that we retrieved
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        '''
        test updating a recipe with put
        '''
        # create sample recipe
        recipe = sample_recipe(user=self.user)
        # create a tag for the sample recipe
        recipe.tags.add(sample_tag(user=self.user))
        # create payload for put update
        payload = {
            'title': 'Chiken Pasta Fettuccine',
            'time_minutes': 35,
            'price': 45,
        }
        # now create the url
        url = detail_recipe_url(recipe.id)
        # make http put request
        self.client.put(url, payload)
        # make sure that values refesh from the db and values have changed
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        # check the minutes have changed
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        # check the price has change
        self.assertEqual(recipe.price, payload['price'])
        # check that the tags assigned are 0 BECAUSE
        # when we omit a field in a PUT request that clears the value
        # of that field.
        # retrieve the tags (which there will be none)
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)
