from django.contrib import admin
from .models import User, Post, Profile

class ProfileAdmin(admin.ModelAdmin):
    filter_horizontal = ("followers",)

class PostAdmin(admin.ModelAdmin):
    filter_horizontal = ("likes",)

# Register your models here.

admin.site.register(User)
admin.site.register(Post, PostAdmin)
admin.site.register(Profile, ProfileAdmin)