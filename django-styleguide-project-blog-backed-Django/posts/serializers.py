from rest_framework import serializers # importing ability to make serializers from Django Rest Framework. Serailizers our what allow us to convert data coming from our database into JSON that we can then send back in a response to the client. They also handle converting the JSON data we are sent in POST(create) and PUT(update) requests to data than can be saved in our database.
from django.contrib.auth import get_user_model # importing our custom User model, we need this to create a UserSerializer which will be used to make sure the owners of our posts and comments are populated so we see the whole user
from .models import Post, Comment, Category # and getting our post and comments models to make serializers for them, adding Category
User = get_user_model() # invoking that get user model function

class UserSerializer(serializers.ModelSerializer): # This user serializer is used to populate a nested owner on a post or comment

    class Meta:
        model = User
        fields = ('id', 'username', 'profile_image')

class CategorySerializer(serializers.ModelSerializer): # For now just making a serializer for populated cateogies. This app doesn't have a route for creating categories so this should be all we need

    class Meta:
        model = Category # setting up the Meta class with its fields as per normal
        fields = ('id', 'name')

class CommentSerializer(serializers.ModelSerializer): # This comment serializer does the same for comments on a post, serializes and populates them, if we didnt do tbhis we would just see a list of comment IDs returned on a post, instead of the full objects in a list.

    class Meta:
        model = Comment
        fields = ('id', 'text', 'owner', 'post')

class PopulatedCommentSerializer(CommentSerializer): # We use this on comment population to show the owner as a seraoilized nested field. note how this is inherting directly from the comment serializer above, and there for has all its meta class and feilds infromation automatically added

    owner = UserSerializer() # use the owner serializer on the owner field of comments

class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('id', 'content', 'image', 'owner', 'comments', 'categories')
        extra_kwargs = {'comments': {'required': False}, 'categories': {'required': False}} # this lines tell the serializer that sometimes, comments wont be there, and thats fine. This is important otherwise when we create a post. it would say we need to make comments along with it. Again this is a USE CASE idea. Maybe you have a nested field that you would want to be required on creation. This just doesn't make sense for comments. we would want to make a post, and then allow users to make comments on that post

class PopulatedPostSerializer(PostSerializer): # again same idea as with the populated comment serilaizer, it inherits from Post Serializer and gets all the meta class and fields from that

    owner = UserSerializer() # any user on the post will be seralized and nested(like .populate() in mongoose)
    comments = PopulatedCommentSerializer(many=True) # same with comments, but in this case, we let the serializer know there will be a list of comments to seralize not just one.
    categories = CategorySerializer(many=True) # and adding out cxategory serliazer
