from rest_framework import serializers
from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    '''
    serializer for tag objects
    '''

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    '''
    Serializer for Ingedient objects
    '''

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    '''
    Serializer for recipe objects
    '''
    # lists ingredients in recipes with their primary key id from their own
    # model. And this is how we want it to appear when listing our recipes.
    # we just want to list id of ingredients, and if we want to retrieve the
    # name of the ingredient we can use the detail API
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
                'id', 'title', 'ingredients', 'tags',
                'time_minutes', 'price', 'link'
            )
        read_only_fields = ('id',)
        # now define primary key related fields (above)


# nest recipe serializer inside of our detail serializer
class RecipeDetailSerializer(RecipeSerializer):
    '''
    Serialize a recipe detail
    '''
    # many=True means we can have many ingredients associated with a recipe
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class RecipeImageSerializer(serializers.ModelSerializer):
    '''
    Serializer for uploading images to recipes
    '''

    class Meta:
        model = Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)
