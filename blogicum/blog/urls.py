from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/<int:pk>/',
         views.PostDetailDetailView.as_view(),
         name='post_detail'
         ),
    path('posts/create/',
         views.CreatePostCreateView.as_view(),
         name='create_post'
         ),
    path('posts/<int:pk>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'
         ),
    path('posts/<int:pk>/delete/',
         views.PostDeleteDeleteView.as_view(),
         name='delete_post'
         ),
    path('posts/<int:pk>/comment/',
         views.AddCommentCreateView.as_view(),
         name='add_comment'
         ),
    path('posts/<int:pk>/edit_comment/<int:id>/',
         views.EditCommentUpdateView.as_view(),
         name='edit_comment'
         ),
    path('posts/<int:pk>/delete_comment/<int:id>/',
         views.DeleteCommentDeleteView.as_view(),
         name='delete_comment'
         ),
    path('category/<slug:category_slug>/',
         views.CategoryPostListView.as_view(),
         name='category_posts'
         ),
    path('profile/<slug:username>/',
         views.ProfileInfoTemplateView.as_view(),
         name='profile'
         ),
    path('profile/<slug:username>/edit/',
         views.EditProfileUpdateView.as_view(),
         name='edit_profile'
         )
]
