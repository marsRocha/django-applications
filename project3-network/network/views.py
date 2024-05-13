from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import json

from .models import User, Post, Profile

from django.core.paginator import Paginator

def index(request):
    return render(request, "network/index.html", {
        "posts": Post.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        firstName = request.POST["name"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user and their profile
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = firstName
            user.save()
            Profile(user=user).save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def following(request):
    return render(request, "network/following.html")

@login_required
def save_post(request):
    if request.method == "POST":
        form = Post(user=request.user, content=request.POST.get("content"))
        form.save()
        return index(request)
    elif request.method == "PUT":
            data = json.loads(request.body)        
            post_id = int(data.get("post_id"))
            new_content = data.get("new_content")

            post = Post.objects.get(pk=post_id)

            # check if user is the one who created the post
            if post.user != request.user:
                return JsonResponse({
                    "result": False
                })

            post.content = new_content
            post.save()
            return JsonResponse({
                "result": True
            })
    else:
        return JsonResponse({
            "result": False
        })


def paginated_posts(request, posts):
    posts = posts.order_by("-date_published").all()
    paginator = Paginator(posts, 10) # Show 10 contacts per page.
    page_obj = paginator.get_page(request.GET.get("current_page"))
    return JsonResponse({
        "posts": [post.serialize(request.user) for post in page_obj],
        "num_pages": paginator.num_pages
        })


def load_posts(request):
    if not request.GET.get("username") is None:
        user = User.objects.get(username=request.GET.get("username"))
        posts = Post.objects.filter(user=user)
    else:
        posts = Post.objects.all()
    return paginated_posts(request, posts)


@login_required
def load_followed_posts(request):
    followings = request.user.get_followings.all().values('user')
    posts = Post.objects.filter(user__in=followings).all()
    return paginated_posts(request, posts)


def profile(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)

    return render(request, "network/profile.html", {
        "user_data": profile.serialize(request.user)
    })


@login_required
def update_follow(request, username):

    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)

    if profile in request.user.get_followings.all():
        profile.followers.remove(request.user)
    else:
        profile.followers.add(request.user)
    profile.save()

    return HttpResponseRedirect(reverse("profile", kwargs={'username': username}))


@login_required
def update_likes(request, post_id):

    post = Post.objects.get(pk=post_id)

    if post in request.user.get_liked_posts.all():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True
    post.save()

    return JsonResponse({
        "likes": post.likes.count(),
        "is_liked": is_liked
    })
