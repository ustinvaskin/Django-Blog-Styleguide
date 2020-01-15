#pylint: disable = no-member
from rest_framework.views import APIView # DRFs generic api view, we then right our own post methods for both a login adn register view
from rest_framework.response import Response # to send json responses
from rest_framework.exceptions import PermissionDenied # some errors, to send when people send the wrong credentials
from rest_framework.permissions import IsAuthenticated # our is authenticated permission, using this on the PROFILE ROUTE ONLY, if you are not doing that you do not need this
from django.contrib.auth import get_user_model # To get the user model with our custom fields
from django.conf import settings # to get our randomly generated secret key from 'project/settings.py'. Going to use this to encode our jwt tokens
import jwt # the jwt token library for python, 'pipenv install pyjwt', so we can generate a token to send back on login
from .serializers import UserSerializer # user serializer, used to make users on register, and send users as json for profile route
User = get_user_model() # invoking the get user model function to get a user model instance

# The views here our very similar to how we did it in Class, but I have added a profile route for getting a user profile

class RegisterView(APIView): # the register route, only has one method, post, as that is all you cna do with register.

    def post(self, request): # post method handler '/register'
        serializer = UserSerializer(data=request.data) # send the data provided in the request to the user seraliser
        if serializer.is_valid(): # see if it creates a user, so does it have all the correct and required fields
            serializer.save() # if it does save it
            return Response({'message': 'Registration Successful'}) # and send a message back of registration successful
        return Response(serializer.errors, status=422) # otherwise, if the data was wrong, send back the errors


class LoginView(APIView): # login view, only has a post method for a request too, also made a custom get user, to check if they user trying to login in exists

    def get_user(self, email): # passing the user attempting to login in the email we have been sent, but this could be by an field, such as username
        try:
            return User.objects.get(email=email) # trying to find the user id by the supllied email, retuning it if found
        except User.DoesNotExist:
            raise PermissionDenied({'message': 'Invalid Credentilais'}) # if not found, send a permission denied response and dont send back a token.

    def post(self, request): # post request for '/login', user provides credentials in JSON format of email and password. If they are correct with will return a JSON webtoken so they can then make authenticated requests to our protected routes. If not we will send back permission denied

        email = request.data.get('email') # getting the email sent in the request
        password = request.data.get('password') # and the password

        user = self.get_user(email) # trying to find the user using our method directly above.

        if not user.check_password(password): # assuming the user was found, checking that the password is correct for that user
            raise PermissionDenied({'message': 'Invalid Credentails'}) # if it isnt correct, send back invalid credentials message, dont send a token

        token = jwt.encode({'sub': user.id}, settings.SECRET_KEY, algorithm='HS256') # If password was correct, we generate a token with the users id, our random secret and the standard jwt algorithim to encode it.

        return Response({'token': token, 'message': f'Welcome back {user.username}'}) # send back that token with a welcome message, concatenting in the username to makle it feel personalised.

class ProfileView(APIView): # one route GET '/profile'

    permission_classes = (IsAuthenticated, ) # profile route requires a user to be signed in, otherwise we would not know which users profile to get. We work out who they are from the token send with the request for the profile

    def get(self, request): # get method to return the user object
        user = User.objects.get(pk=request.user.id) # find the user by their id(primary key, pk). We get the user from the request.user.id. This is set in 'jwt/authentication.py' and is worked out by decoding the jwt token send with the request
        serialized_user = UserSerializer(user) # running that found user through the serialiser to turn it into JSON
        return Response(serialized_user.data) # sending that JSON data
