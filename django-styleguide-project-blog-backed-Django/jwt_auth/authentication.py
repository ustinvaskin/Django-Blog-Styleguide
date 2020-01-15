# pylint: disable = no-member
# We created this file it was not here by default. What we are doing here is making a custom authentication method for ourselves that uses JWT tokens, much the same way our express apps did. What if effectively becomes is our secure route handler. If the user had a valid token, we allow them onto whatever they wanted to, handily attaching the users id to the request on its way, so we can know who they are when they perform actions. I do this all over this app in the 'jwt.views.py' for the profile route (finding the user by the request.user) and in the 'posts/views.py' where I attach the user to created posts.
from rest_framework.authentication import BasicAuthentication # gets the basic authenticaion class from DRF, we extend upon this, see it being passed to our class below
from rest_framework.exceptions import PermissionDenied # an error message to send if the token is invalid or moissing
from django.contrib.auth import get_user_model # accessing our user model
from django.conf import settings # to get our secret key, we used it to encode a jwt token on login, we need it here to decode one that is sent with a request
import jwt # the actual jwt library, again so we can decode a token
User = get_user_model() # using that get user model function to get our custom user model

# This class is almost line for line identical to the secure route handler in our express app from module 3. Even more noticable if you put them side by side. althouth the syntax is slightly different, the actions and logic taken are exactly the same
class JWTAuthentication(BasicAuthentication):

    def authenticate(self, request):
        header = request.headers.get('Authorization') # try to get a authorizaton key from the incoming request headers

        if not header: # If its not there, we return none. This allows users to still interact with unportected routes. In this app at least, that is only register and login routes. again this is USE CASE SPECIFIC
            return None

        if not header.startswith('Bearer'): # if the authorization header is there, but does not start wih the word Bearer
            raise PermissionDenied({'message': 'Invalid Authorization Header'})  # we send a unauthorized message back and stop the request here

        token = header.replace('Bearer ', '') # if it was there we attempt to take just the token from the header

        try: # using pythons try catch syntax to attempt to decode the token and see if its valid
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256']) # we try to decode here
            user = User.objects.get(pk=payload.get('sub')) # and if it works we try to find the user who supplied by the user id we just decoded from the token
        except jwt.exceptions.InvalidTokenError: # but if we couldnt decode it, there was error and we send back this invalid token message
            raise PermissionDenied({'message': 'Invalid Token'})
        except User.DoesNotExist: # or poteniailly we couldnt find a user and send back this error message
            raise PermissionDenied({'message': 'User not found'})

        return (user, token) # if all was good we return our found authenticated user, and the token used, in a tuple. This then attaches itself to the incoming request object. The user will be found as 'request.user' and the token on 'request.auth'. This is then used extensiviely in this app to attach users and owners to resources like comments and posts.
