from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, RegisterSerializer, UserSerializer


# ─── AUTHENTICATION VIEWS ────────────────────────────────────────────


# Register view - creates new user and returns token
class RegisterView(APIView):
    # anyone can access this endpoint
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user  = serializer.save()
            # create token for new user
            token = Token.objects.create(user=user)
            return Response({
                'message' : 'Account created successfully!',
                'token'   : token.key,
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login view - returns token
class LoginView(APIView):
    # anyone can access this endpoint
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            # get or create token for user
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message' : f'Welcome back {username}!',
                'token'   : token.key,
                'username': user.username
            }, status=status.HTTP_200_OK)

        return Response({
            'error': 'Invalid username or password!'
        }, status=status.HTTP_400_BAD_REQUEST)


# Logout view - deletes token
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # delete token to logout
        request.user.auth_token.delete()
        return Response({
            'message': 'Logged out successfully!'
        }, status=status.HTTP_200_OK)


# ─── POST VIEWS ──────────────────────────────────────────────────────


# List all posts and create new post
class PostListCreateView(generics.ListCreateAPIView):
    queryset           = Post.objects.all()
    serializer_class   = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    # search functionality
    filter_backends    = [filters.SearchFilter]
    search_fields      = ['title', 'content', 'author__username']

    # automatically set author to logged in user
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # pass request to serializer for is_liked field
    def get_serializer_context(self):
        return {'request': self.request}


# Get, Update, Delete a single post
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = Post.objects.all()
    serializer_class   = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # pass request to serializer for is_liked field
    def get_serializer_context(self):
        return {'request': self.request}

    # only author can update or delete
    def update(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return Response({
                'error': 'You can only edit your own posts!'
            }, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return Response({
                'error': 'You can only delete your own posts!'
            }, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


# ─── LIKE VIEW ───────────────────────────────────────────────────────


# Like / Unlike a post
class LikePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({
                'error': 'Post not found!'
            }, status=status.HTTP_404_NOT_FOUND)

        if request.user in post.likes.all():
            post.likes.remove(request.user)
            return Response({
                'message'   : 'Post unliked!',
                'likes_count': post.get_likes_count()
            }, status=status.HTTP_200_OK)
        else:
            post.likes.add(request.user)
            return Response({
                'message'   : 'Post liked!',
                'likes_count': post.get_likes_count()
            }, status=status.HTTP_200_OK)


# ─── COMMENT VIEWS ───────────────────────────────────────────────────


# List all comments on a post and create new comment
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class   = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # get comments for specific post only
    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['pk'])

    # automatically set author and post
    def perform_create(self, serializer):
        post = Post.objects.get(pk=self.kwargs['pk'])
        serializer.save(author=self.request.user, post=post)


# Delete a comment
class CommentDeleteView(generics.DestroyAPIView):
    queryset           = Comment.objects.all()
    serializer_class   = CommentSerializer
    permission_classes = [IsAuthenticated]

    # only author can delete their comment
    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return Response({
                'error': 'You can only delete your own comments!'
            }, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


# ─── USER VIEWS ──────────────────────────────────────────────────────


# Get user profile
class UserProfileView(generics.RetrieveAPIView):
    queryset           = User.objects.all()
    serializer_class   = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    # lookup by username instead of id
    lookup_field       = 'username'

    def retrieve(self, request, *args, **kwargs):
        user  = self.get_object()
        posts = Post.objects.filter(author=user)
        return Response({
            'id'         : user.id,
            'username'   : user.username,
            'email'      : user.email,
            'posts_count': posts.count(),
            'posts'      : PostSerializer(
                posts, many=True,
                context={'request': request}
            ).data
        })