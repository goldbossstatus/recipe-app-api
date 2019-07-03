from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient
from recipe import serializers


class TagIngredientAttrViewSet(viewsets.GenericViewSet,
                               mixins.ListModelMixin,
                               mixins.CreateModelMixin):
    '''
    Base Viewset for user owned tags and ingredients attributes
    '''
    authentication_classes = (TokenAuthentication,)
    # requires that token authenticaiton is used, and that the user is auth'd
    permission_classes = (IsAuthenticated,)
    # when you define a listmodel mixin in the generic viewset you need to
    # provide the queryset that you want to return

    def get_queryset(self):
        '''
        return objects for the current authenticated user ONLY
        '''
        # the request object should be passed into the 'self' as a class
        # variable, and the user should be assigned to that, becuase authent'n
        # is required.
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        '''
        create a new object
        '''
        serializer.save(user=self.request.user)


class TagViewSet(TagIngredientAttrViewSet):
    '''
    Manage tags in database
    '''
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(TagIngredientAttrViewSet):
    '''
    Manage Ingredients in the Database
    '''
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
