from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Listing(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    starting_bid = models.FloatField()
    current_bid = models.FloatField(null=True, blank=True)
    date_published = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_listings")
    image = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, default=None, on_delete=models.CASCADE, null=True, blank=True)
    watchers = models.ManyToManyField(User, blank=True, related_name="watched_listings")
    active = models.BooleanField(default=True)
    buyer = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.title} published by \"{self.author}\""


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()

    def __str__(self):
        return f"\"{self.user.username}\" bid EUR {self.amount} on \"{self.listing.title}\""


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    message = models.TextField()
    date_published = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"\"{self.author.username}\" commented \"{self.message}\" on {self.listing.title} listing"