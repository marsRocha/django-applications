from django.contrib import admin
from .models import Listing, User, Bid, Category, Comment

class ListingAdmin(admin.ModelAdmin):
    filter_horizontal = ("watchers",)

# Register your models here.
admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Bid)