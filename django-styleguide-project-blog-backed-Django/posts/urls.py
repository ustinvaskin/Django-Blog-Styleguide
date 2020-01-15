from django.urls import path # we always need to import this from django
from .views import PostListView, PostDetailView, CommentListView, CommentDetailView, CategoryListView # an import all the views we need to hook up to a URL, remeber in Django, the term view is used for what most other frameworks, including express apps, would use the term controller for

urlpatterns = [
    path('posts', PostListView.as_view()), # our just '/posts view(controller), handles GET for Index and POST for Create, actions effecting the ListView
    path('posts/<int:pk>/', PostDetailView.as_view()), # the details view for post, GET show, PUT update, DELETE delete, routes that affect a single post instead of all the posts
    path('posts/<int:pk>/comments/', CommentListView.as_view()), # this is the comments list route , leads to our comments create method view.
    path('posts/<int:pk>/comments/<int:comment_pk>/', CommentDetailView.as_view()), # comment details view only includes a delete method at the moment
    path('categories', CategoryListView.as_view())
]
