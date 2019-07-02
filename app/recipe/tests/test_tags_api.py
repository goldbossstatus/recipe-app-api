from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
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
