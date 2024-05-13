
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("save_post", views.save_post, name="save_post"),
    path("load_posts", views.load_posts, name="load_posts"),
    path("following", views.following, name="following"),
    path("load_followed_posts", views.load_followed_posts, name="load_followed_posts"),
    path("user/<str:username>", views.profile, name="profile"),
    path("user/<str:username>/update_follow", views.update_follow, name="update_follow"),
    path("post/<int:post_id>/update_likes", views.update_likes, name="update_likes")
]
