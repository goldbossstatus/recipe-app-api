from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _


class UserSerializer(serializers.ModelSerializer):
    '''
    serializer for the users object
    '''
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8}
        }

    def create(self, validated_data):
        '''
        create a new user with encrypted password and return it
        '''
        # we are going to call the create_user manager function that we
        # created in the models to create the user so that we know that the
        # password that it stores will be encrypted, otherwise the password
        # that it sets will just be stored in clear text and then the
        # authentication won't work because it is expecting a salt/hash key
        return get_user_model().objects.create_user(**validated_data)
        # unwind validated_data into create_user()

    def update(self, instance, validated_data):
        '''
        Update a user, setting the password correctly and return it
        '''
        # the instance arg will be our model instance, which is linked to our
        # model serializer. The validated_data arg is going to be the class
        # Meta fields that have been passed through the validation already and
        # ready to update.
        # What we want to do is remove the password as an option to update. We
        # do this using the dictionary pop function. Because we are going to be
        # allowing the users to optionally provide a password, we will replace
        # password with the default value of None.
        password = validated_data.pop('password', None)
        # super will call the ModelSerializer update function
        user = super().update(instance, validated_data)
        # if the user provided password
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    '''
    Serializer for the user authentication object
    '''
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    # the validation command/function checks that the inputs are all correct,
    # also validates that the authentication credentials are correct. This is
    # the default token serializer that is built into django rest_framework,
    # we are just modifying it to accept our email address instead of username
    def validate(self, attrs):
        '''
        validate and authenticate the user
        '''
        email = attrs.get('email')
        password = attrs.get('password')
        # this is how you access the content of the request that was made.
        # when a request is made, the django rest_framework it passes the
        # context in nto the serializer the context clause below.
        # And from there we can get ahold of the request that was made.
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        # if we don't return a user/if the authentication failed....
        if not user:
            message = _('Oops! Provided invalid credentials!')
            # raise a validation error and django rest_framework knows how to
            # handle this error by passing the error as a 400 response as well
            # as the message back to the user
            raise serializers.ValidationError(message, code='authentication')
            # whenever you are overriding the validate function you must
            # return the values at the end after the alidation is successfull
        attrs['user'] = user
        return attrs
