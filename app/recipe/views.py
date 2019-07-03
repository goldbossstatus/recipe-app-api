from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient
from recipe import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    '''
    Manage tags in databse
    '''
    #
    authentication_classes = (TokenAuthentication,)
    # requires that token authenticaiton is used, and that the user is auth'd
    permission_classes = (IsAuthenticated,)
    # when you define a listmodel mixin in the generic viewset you need to
    # provide the queryset that you want to return
    queryset = Tag.objects.all()
    # add serializer class
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        '''
        Return Objects for the current authenticated user only
        '''
        # the request object should be passed into the 'self' as a class
        # variable, and the user should be assigned to that, becuase authent'n
        # is required.
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        '''
        Create a new tag per specific user
        '''
        #
        serializer.save(user=self.request.user)


class IngredientViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    '''
    Manage Ingredients in the Database
    '''
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    def get_queryset(self):
        '''
        Return objects for the current authenticated user only
        '''
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        '''
        Create a new ingredient per specific user
        '''
        serializer.save(user=self.request.user)
