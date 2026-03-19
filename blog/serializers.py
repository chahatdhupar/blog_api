from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment


# User serializer - converts User model to JSON
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'email']


# Comment serializer - converts Comment model to JSON
class CommentSerializer(serializers.ModelSerializer):
    # show username instead of user id
    author = UserSerializer(read_only=True)

    class Meta:
        model  = Comment
        fields = ['id', 'author', 'content', 'created_at']
        # read_only_fields means these cannot be changed via API
        read_only_fields = ['author', 'created_at']


# Post serializer - converts Post model to JSON
class PostSerializer(serializers.ModelSerializer):
    # show full author details instead of just id
    author = UserSerializer(read_only=True)

    # show all comments inside post
    comments = CommentSerializer(many=True, read_only=True)

    # show likes count
    likes_count = serializers.SerializerMethodField()

    # show if current user liked this post
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model  = Post
        fields = [
            'id', 'author', 'title', 'content',
            'likes_count', 'is_liked', 'comments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

    # custom method to get likes count
    def get_likes_count(self, obj):
        return obj.get_likes_count()

    # custom method to check if current user liked this post
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.likes.all()
        return False


# Register serializer - for creating new users
class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password1', 'password2']

    # validate passwords match
    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Passwords do not match!')
        return data

    # create user with hashed password
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password1']
        )
        return user