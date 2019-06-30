from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@admin.com',
            password='password123',
        )
        # client helper function allows us to log a user in with
        # the django auth
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='password123',
            name='Test user full name'
        )

    def test_users_listed(self):
        '''
        Test that users are listed on user page
        '''
        # this url is defined in the django admin documentation, which will
        # generate the url for our list user page.
        url = reverse('admin:core_user_changelist')
        # this will perform a http get request on the client
        response = self.client.get(url)
        # this assertion will check that the response has a certain item,
        # also checks that the response comes back 200, and looks into the
        # actual content that is rendered
        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        '''
        Test that the user edit page works
        '''
        url = reverse('admin:core_user_change', args=[self.user.id])
        # /admin/core/user/1
        response = self.client.get(url)
        # test that the page renders OK
        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self):
        '''
        Test that the create user page works
        '''
        url = reverse('admin:core_user_add')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
