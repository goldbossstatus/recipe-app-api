import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.conf import settings


def recipe_image_filepath(instance, filename):
    '''generate file path for new recipe image'''
    # strip the extention part of the filename (everything after last dot)
    # slice the list and return the last item, so this will return the
    # extension of the file name
    extension = filename.split('.')[-1]
    # now make the file name using the f string feature
    # so this creates a function with the NEW uuid (uuid.uuid4 function) and
    # then keeps the extension of the file that was passed in.
    filename = f'{uuid.uuid4()}.{extension}'
    # now 'join' this up the to the desitination path we want to store the file
    return os.path.join('uploads/recipe/', filename)


class UserManager(BaseUserManager):

        def create_user(self, email, password=None, **extra_fields):
            '''
            Creates and saves a new user
            '''
            # this is the statement that raises valueerror for the
            # test_new_user_invalid_email func in test_models
            if not email:
                raise ValueError('Users must have an email address')
            # normalizemail is a helperfunction that comes with BaseUserManager
            user = \
                self.model(email=self.normalize_email(email), **extra_fields)
            # use the setpassword helper function to encrypt the password
            user.set_password(password)
            # using=self._db supports multiple databases
            user.save(using=self._db)

            return user

        def create_superuser(self, email, password):
            '''
            Creates and saves a new superuser
            '''
            # use our create_user func we made above, no need to type again
            user = self.create_user(email, password)
            user.is_staff = True
            user.is_superuser = True
            # because we modified the user we need to save it below
            user.save(using=self._db)

            return user


class User(AbstractBaseUser, PermissionsMixin):
    '''
    Custom User model that supports using email instead of username
    '''
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    '''
    Tag to be used for a recipe
    '''
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        '''
        Add string representation of the model
        '''
        return self.name


class Ingredient(models.Model):
    '''
    Ingredient to be used in a recipe
    '''
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    '''
    Recipe object
    '''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    # provide name of the class in a string
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')
    image = models.ImageField(null=True, upload_to=recipe_image_filepath)

    def __str__(self):
        return self.title
