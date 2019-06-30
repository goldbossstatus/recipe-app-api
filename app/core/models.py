from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin


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
