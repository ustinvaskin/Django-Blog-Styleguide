# We use this file to register models to become available on the Django admin site. That gives us full CRUD functuinality over our models, even withoout a view or controller set up yet.
from django.contrib import admin # this is here by default when django generates the files
from .models import Post, Comment, Category # and importing our two models from this app that we want to add to the admin panel

# Register your models here.
admin.site.register(Post) # the syntax to register the model
admin.site.register(Comment) # and again for comments
admin.site.register(Category) # finally registered the category as well
