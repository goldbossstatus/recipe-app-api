# python function that allows you to generate temp files
import tempfile
import os
# pillow requirements importing our image class which will then let us create
# test images which we can then upload to our API
from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


# /api/recipe/recipes
RECIPES_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    '''
    Return URL for recipe image upload
    '''
    # the name we will give our custom URL for our endpoint
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


# /api/recipe/recipes/2 (example)
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


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        # create client
        self.client = APIClient()
        # create user
        self.user = get_user_model().objects.create_user(
            'test@america.com',
            'testpassword'
        )
        # authenticate user
        self.client.force_authenticate(self.user)
        # create recipe
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        # We want to make sure that our filesystem is kept clean after our
        # tests, and this means REMOVING all of the test files that we create.
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        '''
        Test uploading an image to recipe
        '''
        # create the url using the sample recipe in the setUp
        url = image_upload_url(self.recipe.id)
        # creates a names temporary file in the system at a random location,
        # (usually in the /temp folder)
        # this creates a temporary file in the system that we can then write
        # too, and after you exit the context manager, (outside the
        # with statement) it will automatically remove the file
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            # creates an image with the Image class that we uploaded from
            # the PIL Library,   black square that is 10 pixels by 10 pixels
            image = Image.new('RGB', (10, 10))
            # save the image to our file, and then write the full map that
            # you want to save it as.
            image.save(ntf, format='JPEG')
            # this is the way the pythton reads files, so we use seek function
            # to set the pointer back to the beginning of the file, as if we
            # jst opened it
            ntf.seek(0)
            # request with image payload and add the format option to our post
            # to tell django that we want to make a multipart form request.
            # A FORM THAT CONSISTS OF DATA. By default it would be a form that
            # that just consists of a json object, but we want to post data
            res = self.client.post(url, {'image': ntf}, format='multipart')
            # now run assertions
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # now check that image from payload is in the response
        self.assertIn('image', res.data)
        # check that path exists for image that is saved to model
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        '''
        Test uploading an invalid image
        '''
        # create url
        url = image_upload_url(self.recipe.id)
        # create post request with invalid payload
        res = self.client.post(url, {'image': 'not image'}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        '''
        Test returning recipes with specific tags
        '''
        # create three recipes, two of them will have tags assigned, and one
        # of them will not have the tag assigned.
        # make the request with the filter parameters for the tags and ensure
        # that the results returned match the ones with the tags and exclude
        # the one without the tags
        recipe1 = sample_recipe(user=self.user, title='Chicken Lime Soup')
        recipe2 = sample_recipe(user=self.user, title='Salmon with lemon')
        tag1 = sample_tag(user=self.user, name='soup')
        tag2 = sample_tag(user=self.user, name='fish')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        recipe3 = sample_recipe(user=self.user, title='Tenderloin')

        # so now make request for soup and fish options in our database
        response = self.client.get(
            RECIPES_URL,
            # pass get parameters to a get request using the test client by
            # just passing in a dictionary of the values you wish to add as
            # get parameters.
            # the way the filter feature is being desined is that if you want
            # to filter by tags,  you simply pass a get parameter wiht a comma
            # separated list of the tags ids you wish to filter by
            {'tags': f'{tag1.id},{tag2.id}'}
        )
        # serialize the recipes, and see if they exist in the responses return
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

    def test_filter_recipes_by_ingredient(self):
        '''
        Test returning recipes with specific ingredients
        '''
        # create sample recipes
        recipe1 = sample_recipe(user=self.user, title='French Dip')
        recipe2 = sample_recipe(user=self.user, title='Mac n cheese Bake')
        # create sample ingredients
        ingredient1 = sample_ingredient(user=self.user, name='Au Jus')
        ingredient2 = sample_ingredient(user=self.user, name='Sharp Cheddar')
        # add ingredients to recipe
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        # now make recipe without any ingredients added to it
        recipe3 = sample_recipe(user=self.user, title='Chicken Parmesean')

        response = self.client.get(
            RECIPES_URL,
            {'ingredients': f'{ingredient1.id},{ingredient2.id}'},
        )
        # serialize the objects
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        # make assertions
        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)
