from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/new", views.create, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("listing/close/<int:listing_id>", views.close_listing, name="close"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/update", views.watchlist_update, name="watchlist_update"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("category", views.category, name="category")
]
