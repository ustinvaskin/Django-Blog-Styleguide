#pylint: disable = no-member, arguments-differ
from rest_framework import serializers # importing the serlaizers funcionality from django rest framework
from django.contrib.auth import get_user_model # method to get the user model
import django.contrib.auth.password_validation as validations # this is a built in part of django we can use to validate passwords out of the box
from django.contrib.auth.hashers import make_password # built in part of django we can use to hash our passwords
from django.core.exceptions import ValidationError # and error we can use if password and confirmation dont mate
from django.apps import apps # this is the method used to import a model from another app. We can not always import it directly, as this creates what is called a circular import which can cause issues, to many things being imported all over the place. This is safer method to do it
User = get_user_model() # invoking get user model to get our custom User model instance.
Post = apps.get_model('posts', 'Post') # importing the Post model to create a post searlizer here. Importing the exisiting one from the posts project would again cause circular import issues.

class PostSerializer(serializers.ModelSerializer): # We make this quick little serializer to populate a posts field on our user. This gives the nice functionality on the profile route that return our user object, along with all the posts they've made

    class Meta:
        model = Post
        fields = ('id', 'content', 'image')


class UserSerializer(serializers.ModelSerializer): # Our user serializer, as well as converting our user objects to and from JSON we use a custom validate method inside here to check that the pasword and confirmation match when a User tries to sign up

    password = serializers.CharField(write_only=True) # the write only parts on these fields ensure our password and confirmation will never be sent out wiht he profile or login views.
    password_confirmation = serializers.CharField(write_only=True)
    posts = PostSerializer(many=True, required=False) # registering the post serializer so we can show a nested list of populated posts.

    def validate(self, data): # the validate method user on our passwords to see if they match

        password = data.pop('password') # get the password from the request
        password_confirmation = data.pop('password_confirmation') # and the confirmtion fields

        if password != password_confirmation: # If they don't match, we send back an error to the client
            raise ValidationError({'password_confirmation': 'does not match'})

        try: # This uses the inbuilt django password validator, checks length and commonality. 
            validations.validate_password(password=password)
        except ValidationError as err: # if it doesnt pass, we send back the errors
            raise serializers.ValidationError({'password': err.messages})

        data['password'] = make_password(password) # IF all was good, we hash the password with the inbuilt make_password function
        return data

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirmation', 'profile_image', 'posts') # the fields for our user model, password amnd password confirmation are included as they need to be there when we create a user, but they are never sent in a request for one. Note we also include the posts field to show the users posts.
