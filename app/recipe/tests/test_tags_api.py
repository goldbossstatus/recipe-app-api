from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer


TAGS_URLS = reverse('recipe:tag-list')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicTagsApiTests(TestCase):
    '''
    Test the publicly available tags API
    '''

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        '''
        Test that login is required for retrieving tags
        '''
        # simulate attempt to retrieve without authentication
        response = self.client.get(TAGS_URLS)
        # test that correct server code is returned
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    '''
    Test that tag API requires authentication
    '''
    def setUp(self):
        self.user = create_user(
            email='test@america.com',
            password='testpassword',
            name='Test Name'
        )
        # create re-usable client
        self.client = APIClient()
        # use the force authenticate method
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        '''
        Test retrieving tags
        '''
        # create sample tags to retrieve
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Lunch')
        # simulate the attempt of the client to retrieve
        response = self.client.get(TAGS_URLS)
        # call a query to retrieve the tags
        tags = Tag.objects.all().order_by('-name')
        # create a serializer, must specifiy that many=True or the serializer
        # will assume that you only want to serialize a single object
        serializer = TagSerializer(tags, many=True)
        # check proper server code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check that all data has been properly retrieved
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        '''
        Test that tags returned are for the authenticated user
        '''
        payload = {
            'email': 'test@user2.com',
            'password': 'testpassword',
            'name': 'Test Name'
        }
        # create another user
        user2 = create_user(**payload)
        # create a tag for user 2 we just created
        Tag.objects.create(user=user2, name='Fruity')
        # create a tag for our authenticated user we created in setUp
        tag = Tag.objects.create(user=self.user, name='Italian')
        # create a response that simulates setUp user attempting to retrieve
        # there own tag object
        response = self.client.get(TAGS_URLS)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn(response.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        '''
        Test creating a new Tag
        '''
        # create sample tag paylad
        payload = {
            'name': 'Test Tag',
        }
        # simulate HTTP Post with payload
        self.client.post(TAGS_URLS, payload)
        # filter all tags with the user that is the authenticated user, and
        # with the name that we created in our test payload.
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name'],
            ).exists()
        # the .exists() will turn this whole thing into a boolean, if if does
        # exist it will be true and vicer versa
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        '''
        Test creating a new tag with invalid payload
        '''
        payload = {'name': ''}
        response = self.client.post(TAGS_URLS, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        '''
        Test filtering tags by those assigned to recipes
        '''
        # create two tags, assign one of those tags to a recipe, leave the
        # other tag unassigned, and make http get call with the assigned_only
        # filter, and then make sure only the tag assigned to a recipe
        # gets returned
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Huevos Rancheros',
            time_minutes=8,
            price=10,
            user=self.user,
        )
        recipe.tags.add(tag1)
        # we are calling our filter assigned_only, and pass in a 1, which will
        # be evaluated by the prgraam as True, and it will filter by the tags
        # that are assigned only
        response = self.client.get(TAGS_URLS, {'assigned_only': 1})
        # create a serailizer so we can verify if they are in the response
        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        # make sure the serializer for breakfast tag is included in response
        self.assertIn(serializer1.data, response.data)
        # make sure lunch tag not return becasue it is not assigned to a recipe
        self.assertNotIn(serializer2.data, response.data)

    def test_retrtieve_tags_assigned_unique(self):
        '''
        Test filtering tags assigned unique items, this applies to a tag
        potentially being in multiple recipes, we want to make sure we return
        UNIQUE items, so one response per tag/recipe relation
        '''
        # create
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Dinner')
        # create two recipes
        recipe1 = Recipe.objects.create(
            title='French Toast',
            time_minutes=15,
            price=10,
            user=self.user
        )
        # assign first tag to recipe
        recipe1.tags.add(tag1)
        # create second recipe
        recipe2 = Recipe.objects.create(
            title=' Second Breakfast',
            time_minutes=5,
            price=3,
            user=self.user,
        )
        # assign recipe 2 to tag 1 as well
        recipe2.tags.add(tag1)
        # make call to retrieve tags ONLY assigned to a recipe
        response = self.client.get(TAGS_URLS, {'assigned_only': 1})
        # make sure to return only ONE tag object (BREAKFAST)
        self.assertEqual(len(response.data), 1)
