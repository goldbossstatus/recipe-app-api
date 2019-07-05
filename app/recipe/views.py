from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
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


class RecipeViewSet(viewsets.ModelViewSet):
    '''
    Manage Recipes in the databse
    '''
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        '''
        Retrieve the recipes for the authenticate user
        '''
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        '''
        return appropriate serializer class
        '''
        # check the self.action class variable which will contain the action
        # that is being used for our current request
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        # if the retrieve or upload is not called, we will just return the
        # recipe, rather than the recipe DETAIL
        return self.serializer_class

    def perform_create(self, serializer):
        '''
        Create a new recipe
        '''
        # this is what need to do to make our test pass becuase the model
        # viewset allows you to create objects out of the box. So the only
        # thing we need to do is assign the authenticated user to that model
        # once it has been created
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        '''
        Upload an image to a recipe with a custom action
        '''
        # retrieve recipe object, get_object() will get the object that is
        # being acesses based on the id in the url
        recipe = self.get_object()
        # create serializer
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )
        # validate the data to make sure everything is correct
        if serializer.is_valid():
            # because we are using a model serialier, in our Recipe serializer
            # you can use the save funciton to save the object. This
            # performs a save on the recipe model with the updataed data
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        # add default behavior which is assuming that we don't return response,
        return Response(
            # django performs auto validation for us and if there are errors
            # django will generate a list/description of all of the errors
            serializer.errors,
            # now assign the request to the response
            status=status.HTTP_400_BAD_REQUEST
        )
