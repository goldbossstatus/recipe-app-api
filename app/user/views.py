from user.serializers import UserSerializer, AuthTokenSerializer
# this view comes with the django rest_framework, premade that allows us to
# easily make an api that creates an object in a database using the serializer
# that we are going to provide.
from rest_framework import generics, authentication, permissions
# if you are using the standard username and password to authenticate, it is
# very easy to switch this on, and add them straight to the urls, in our case
# we just need to make a few changes to the class variables
from rest_framework.authtoken.views import ObtainAuthToken
# for default renderer classes
from rest_framework.settings import api_settings


class CreateUserView(generics.CreateAPIView):
    '''
    Create a new user in the system
    '''
    # we need specify a class variable that points to the serializer class
    # that we want to use to create the object.
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    '''
    Create a new auth token for user
    '''
    # serializer we just created
    serializer_class = AuthTokenSerializer
    # sets renderer so we can view this endpoint in the browser with the
    # browser api. If we DONT do this then we have to use a tool such as
    # C-URL to make the http post request. And now if we ever change the
    # renderer class and want to use a different class to render we can
    # just change it in our settings and it will update automatically.
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    '''
    Manage the authenticated user
    '''
    serializer_class = UserSerializer
    # authentication is the mechansim of which the authentication happens,
    # and we are going to use token authentication.
    # Permission are the levels of access that the user has. And the only
    # permission that we are going to add is that the user must be
    # authenticated to use the API (just logged in)
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    # now add a get object function to our api view
    # we are going to override the getobject and return the authenticate user

    def get_object(self):
        '''
        Retrieve and return authenticated user
        '''
        # when the get_object() is called the request will have the user
        # attached to it BECAUSE of the above authentication classes. Because
        # we have the authentication class that takes care of getting the
        # authenticated user and assigning it to a request.
        # (THIS IS PART OF THE DJANGO REST FRAMEWORK)
        return self.request.user
