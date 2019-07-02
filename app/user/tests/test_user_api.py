from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# rest_framework test helper tools
# test client that we can use to make requests to our api and check responses
from rest_framework.test import APIClient
# module that contains helper status codes i.e., http 200 OK
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    '''
    Test the users API (public)
    '''

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        '''
        Test creating user with valid payload is successful
        '''
        payload = {
            'email': 'test@america.com',
            'password': 'testpassword',
            'name': 'Test name'
        }
        # http post request to our client to our url for creating users
        response = self.client.post(CREATE_USER_URL, payload)
        # test that the outcome is a 201 CREATED response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # if this get the user data (dict) we know that the user was created
        # call an http get request for the user we just created
        user = get_user_model().objects.get(**response.data)
        # test for check password
        self.assertTrue(user.check_password(payload['password']))
        # now we want to check that the password is not returned as a part of
        # the user object, as this is a security threat.
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        '''
        Test creating a user that already exists results in a failure
        '''
        payload = {
            'email': 'test@america.com',
            'password': 'testpassword',
            'name': 'test name',
        }
        # we will simulate creating a user that already exists
        create_user(**payload)
        # simulate an HTTP POST request for creating a user that
        # already exists
        response = self.client.post(CREATE_USER_URL, payload)
        # test that we get the proper status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        '''
        Test that the password must be more than 8 characters
        '''
        payload = {
            'email': 'test@america.com',
            'password': 'pw',
            'name': 'test name',
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # check that the user was never created
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        # the test will fail if the user does exist
        self.assertFalse(user_exists)

    def create_token_for_user(self):
        '''
        test that a token is created for the user
        '''
        payload = {
            'email': 'test@america.com',
            'password': 'testpassword',
            'name': 'Test Name',
        }
        # now create a user that MATCHES this payload/authentication so
        # we can test against that user
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)
        # the response for our post request.data should include a key 'token'
        # we are relying on djangos own built in authentication system
        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dont_create_token_invalid_credentials(self):
        '''
        test that token is not created if invalid credentials are provided
        '''
        # create a valid user object
        create_user(
            email='test@america.com',
            password='testpassword',
            name='test name'
        )
        # simulate an invalid credentials user attempt to check against valid
        # user object that we created
        payload = {
            'email': 'test@america.com',
            'password': 'invalid',
            'name': 'Test name',
        }
        # make post request response
        response = self.client.post(TOKEN_URL, payload)
        # make sure that the token is not in the response data
        self.assertNotIn('token', response.data)
        # make sure that a 400 is sent back
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dont_create_token_no_user(self):
        '''
        test that token is not created if userr doesn't exist
        '''
        payload = {
            'email': 'test@america.com',
            'password': 'testpassword',
            'name': 'Test Name',
        }
        # make the post request WITHOUT creating a user object
        response = self.client.post(TOKEN_URL, payload)
        # test that token is not returned
        self.assertNotIn('token', response.data)
        # test that 400 is sent back to the request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dont_create_token_missing_field(self):
        '''
        test that email and password are required
        '''
        # simulate missing fields post request
        payload = {
            'email': 'fakeeamail',
            'password': '',
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        '''
        Test that authentication is required for users
        '''
        # simulate an attempt to retrieve user without a token
        response = self.client.get(ME_URL)
        # tests that if you call the url without any authentication it
        # returns an HTTP_401_UNAUTHORIZED
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    '''
    Test API requests that require authentication
    '''

    # create authentication for each test that we do, which can be done once
    # in the setUp, as this function gets ran prior to any tests
    def setUp(self):
        self.user = create_user(
            email='test@america.com',
            password='testpassword',
            name='Test name'
        )
        # create re-usable client
        self.client = APIClient()
        # use the force authenticate method, which is a helper function
        # makes it really easy to simulate making authenticated requests
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_successful(self):
        '''
        Test that retrieves profile for logged in user
        '''
        #
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # remeber NOT to make retrieving the password an option,
        # as this opens unnessacary vulnerabilities
        self.assertEqual(response.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        '''
        Test that POST is not allowed on the me url
        '''
        # simulate an example post
        response = self.client.post(ME_URL, {})

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        '''
        Test updating the user profile for authenticated user
        '''
        # create/simulate new payload
        payload = {
            'email': 'test@zappos.com',
            'password': 'zappospassword',
            'name': 'Zappos'
        }
        # make the request
        response = self.client.patch(ME_URL, payload)
        # now use the refresh_from_db helper function on our user to UPDATE the
        # user with the LATEST values from the database.
        self.user.refresh_from_db()
        # now validate that each of the values we provided were updated
        self.assertEqual(self.user.name, payload['name'])
        # now check that password was updated using the helper function
        self.assertTrue(self.user.check_password, payload['password'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
