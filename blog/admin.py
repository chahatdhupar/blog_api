from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display  = ['title', 'author', 'get_likes_count', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    list_filter   = ['created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ['author', 'post', 'created_at']
    search_fields = ['author__username', 'content']