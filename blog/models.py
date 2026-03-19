from django.db import models
from django.contrib.auth.models import User


# Post model - stores blog posts
class Post(models.Model):
    author  = models.ForeignKey(User, on_delete=models.CASCADE)
    title   = models.CharField(max_length=200)
    content = models.TextField()
    likes   = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_likes_count(self):
        return self.likes.count()

    class Meta:
        ordering = ['-created_at']    # newest posts first


# Comment model - stores comments on posts
class Comment(models.Model):
    post    = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author  = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} on {self.post.title}"

    class Meta:
        ordering = ['created_at']    # oldest comments first