from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date_published = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, blank=True, related_name="get_liked_posts")

    def serialize(self, user):
        return {
            "id": self.id,
            "author_id": self.user.id,
            "author_name": self.user.first_name,
            "author_username": self.user.username,
            "content": self.content,
            "date_published": self.date_published.strftime("%b %d %Y, %I:%M %p"),
            "liked": user in self.likes.all(),
            "likes": self.likes.count(),
            "can_edit": self.user == user
        }

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, blank=True, related_name="get_followings")

    def serialize(self, user):
        return {
            "id": self.id,
            "user_id": self.user.id,
            "user_name": self.user.first_name,
            "user_username": self.user.username,
            "followers": self.followers.count(),
            "following": self.user.get_followings.count(),
            "is_following": user.is_authenticated and user in self.followers.all()
        }