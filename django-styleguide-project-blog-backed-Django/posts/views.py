# pylint: disable=no-member
from rest_framework.response import Response # response function from DRF so we can send JSON responses
from rest_framework.views import APIView # instead of using the generic views from DRF, I'm using the basic API view, all though this means more work in writing out the controllers(remember in Django view = controlller from express, where the logic happens) it means more control over the functionality. Again this is a decision to make based on use case for YOUR app.
from rest_framework.permissions import IsAuthenticated # our IsAuthenticated permission import, there are a few different options here
from rest_framework.status import HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED # importing some custom response status codes from django
from .models import Post, Comment, Category # Our Post Model
from .serializers import PopulatedPostSerializer, PostSerializer, CommentSerializer, CategorySerializer# And our serialisers

class PostListView(APIView): # Our List view methods, GET and POST, we have to define these ourselves when just using DRF APIView, url would be just '/posts'

    permission_classes = (IsAuthenticated, ) # is a built in Django permission, means all actions require a token passed, again, this is use case specific

    def get(self, _request): # method to handle GET requests to the list view, the INDEX
        posts = Post.objects.all() # get all the posts from the DB
        serialized_posts = PopulatedPostSerializer(posts, many=True) # serialise those posts into JSON, letting it know to expect a list of posts as this is an INDEX route!!!!!
        return Response(serialized_posts.data) # send that serialised list of posts back as the response to the client

    # Note - don't get confused here by the fact the method is called post and we are creating posts. The method name refers to HTTP verd POST, which is what we use to send a create request, our other post, is because tht is the name of the post resource of our blog app
    def post(self, request): # method to handle POST requests to create a new post.
        request.data['owner'] = request.user.id # attach the owner id to the post, we get this from the authentication class, our user it attached as request.user
        post = PostSerializer(data=request.data) # we pass the data we have been send with the request(the json body of the POST request to '/posts', which should contain a valid object with all the correct fields)
        if post.is_valid(): # we can then use this in built is valid function, to see if your request data was right, and included everything it needed to
            post.save() # If is valid comes back as true, we save the post. This creates it in the database
            return Response(post.data, status=HTTP_201_CREATED) # we then send back the newly created post in the response to client, the data object of the post is the JSON data
        return Response(post.errors, status=HTTP_422_UNPROCESSABLE_ENTITY) # if the post is not valid, we send the post with its errors object, this contains information about what fields would of been missing/have mistakes in them alone with a 422 sttus code

class PostDetailView(APIView): # Our post details view handles all methods that our about a specific post, not the whole collection. So the url for these methods would be 'posts/id'

    permission_classes = (IsAuthenticated, ) # again using the same permission classes, so all routes must be authenticated with a token

    def get(self, _request, pk): # GET method for 'posts/id' this is our show route, getting one post.
        post = Post.objects.get(pk=pk) # ffind the post though its primary key, this is passed from the url in the request, see 'posts/urls.py' for more
        serialized_post = PopulatedPostSerializer(post) # run the found post through the serializer to turn it to json
        return Response(serialized_post.data) # send that json back to client

    def put(self, request, pk):
        request.data['owner'] = request.user.id # since all the information must be present for a put request, we have to attach the user as the owner
        # finding the post we want to update by its primary key (if from the URL)
        post = Post.objects.get(pk=pk)
        if post.owner.id != request.user.id:  # quick check to see if the user making the request is the same user who created the post, if not don't allow updates
            return Response(status=HTTP_401_UNAUTHORIZED)
        updated_post = PostSerializer(post, data=request.data) # we run that post through the seraliser, with the data from the reuqet(the fields to change), this merges the changes in and validates them for us
        if updated_post.is_valid(): # again we check to see if that updated version is valid (ie follows all the rules of the model, what is/isnt required)
            updated_post.save() # save that updated post if it was valid
            return Response(updated_post.data) # and send it back to client
        return Response(updated_post.errors, status=HTTP_422_UNPROCESSABLE_ENTITY) # if it wasnt valid , send back the errors in response with a 422 status

    def delete(self, request, pk): # And our delete method for 'posts/id', deleting one post
        post = Post.objects.get(pk=pk) # find the post to delete
        if post.owner.id != request.user.id: # quick check to see if the user making the request if the same user who created the post, if not don't allow deletes
            return Response(status=HTTP_401_UNAUTHORIZED)
        post.delete() # call the inbuilt delete method on it
        return Response(status=HTTP_204_NO_CONTENT) # send a 204 no content response to the client to show it has been deleted

class CommentListView(APIView): # Our comments view methods, I won't be making a get request to all comments, but will have a POST request method, the url for tbhis route will be thje same as comments from our express app. 'posts/:id/comments'. Although this isnt strictly neccesary and we could of not done it, I think this URL pattern looks familiar and explains what we are trying to effect.

    permission_classes = (IsAuthenticated, ) # same permission classes as the rest of our views, must be logged in

    def post(self, request, pk): # post request method to create a new comment
        request.data['owner'] = request.user.id # attach the current user from the token to the comment
        request.data['post'] = pk # attach the post id from the url to comment
        comment = CommentSerializer(data=request.data) # seralize the comment
        if comment.is_valid(): # if the comment is valid
            comment.save() # save the comment
            post = Post.objects.get(pk=pk) # find the post attributed to the comment
            serialized_post = PopulatedPostSerializer(post) # serialise that post
            return Response(serialized_post.data) # send back the post with the new comment attached
        return Response(comment.errors, status=HTTP_422_UNPROCESSABLE_ENTITY) # send back any errors from the comment if it wasnt valid

class CommentDetailView(APIView):

    permission_classes = (IsAuthenticated, )

    # The URL for this view is to 'api/posts/post_id/comments/comment_id', the comment id is passed as a named argument
    def delete(self, request, comment_pk, **kwargs): # we can ignore the comment and post id here,
        comment = Comment.objects.get(pk=comment_pk) # find the comment by its id
        if comment.owner.id != request.user.id: # check if the request came from the comment owner
            return Response(status=HTTP_401_UNAUTHORIZED) # if not the comment owner send back unauthorized
        comment.delete() # delete it
        return Response(status=HTTP_204_NO_CONTENT) # send back no content response to the client

class CategoryListView(APIView): # Just going to make a list view for the categories. Not going to nest posts in them or anything like that and only going to make a GET method for this view. The main task it will really fulfill will be to populate dropdowns in the forms for category options
    permission_classes = (IsAuthenticated, )

    def get(self, _request): # as stated just a GET (index) for this view
        categories = Category.objects.all() # get  all the categories
        serialized_categories = CategorySerializer(categories, many=True) # serialize them
        return Response(serialized_categories.data) # send them back to the client
