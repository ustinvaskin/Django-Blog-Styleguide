from django.db import models # normal model import from django
from django.contrib.auth.models import AbstractUser # This allows us to extend the default user model given to us by Django


class User(AbstractUser):

    email = models.CharField(max_length=50, unique=True) # overwriting the already exisiting email method, to make it required and need tobe unique
    profile_image = models.CharField(max_length=500) # adding a profile image field
