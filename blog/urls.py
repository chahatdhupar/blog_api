from django.urls import path
from . import views

urlpatterns = [

    # authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # post endpoints
    path('posts/', views.PostListCreateView.as_view(), name='post_list'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/like/', views.LikePostView.as_view(), name='like_post'),

    # comment endpoints
    path('posts/<int:pk>/comments/', views.CommentListCreateView.as_view(), name='comment_list'),
    path('comments/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),

    # user endpoints
    path('users/<str:username>/', views.UserProfileView.as_view(), name='user_profile'),
]
