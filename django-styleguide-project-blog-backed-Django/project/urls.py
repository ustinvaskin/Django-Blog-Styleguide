from django.contrib import admin
from django.urls import path, include # this here by default, but we add the imprt of include, that lets us reference our apps as strings below

urlpatterns = [
    path('admin/', admin.site.urls), # this is also here by default, the url for django admin site
    path('api/', include('jwt_auth.urls')), # prefix api and sending it of to our jwt_auth urls, login, register and profile
    path('api/', include('posts.urls')) # prefixing api and sending it off to our posts urls
]
