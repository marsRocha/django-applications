from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Category, Comment, Bid


def index(request):
    return render(request, "auctions/index.html", {
        "categories": Category.objects.all(),
        "listings": Listing.objects.filter(active=True)
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create(request):
    if request.method == "POST":
        # get form data
        form = request.POST
        user = request.user
        title = form.get("title")
        description = form.get("description")
        starting_bid = form.get("starting_bid")
        description = form.get("description")
        image = form.get("image")
        category = Category.objects.get(pk=int(form.get("category")))
        Listing.objects.create(title=title, description=description, starting_bid=starting_bid, author=user, image=image, category=category)
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, "auctions/createListing.html", {
            "categories": Category.objects.all()
        })


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    comments = Comment.objects.filter(listing=listing)

    if request.user.is_authenticated:
        is_watched = False
        my_bid = is_my_bid(listing, request.user)
        if request.user in listing.watchers.all():
            is_watched = True
        
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "is_my_bid": my_bid,
            "comments": comments,
            "is_watched": is_watched
        })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": comments
        })


def is_watched(listing, user):
    if user in listing.watchers.all():
        return True
    else:
        return False


def is_my_bid(listing, user):
    if listing.current_bid is not None:
        res = Bid.objects.filter(listing=listing, user=user).last()
        if res is not None and res.amount == listing.current_bid:
            return True
    else:
        return False


@login_required
def watchlist_update(request):
    form = request.POST
    listing = Listing.objects.get(pk=form.get("listing_id"))

    # check if it shoudl remove or add listing to the user's watchlist
    if request.user in listing.watchers.all():
        listing.watchers.remove(request.user)
    else:
        listing.watchers.add(request.user)

    return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing.id}))


@login_required
def bid(request, listing_id):
    form = request.POST
    listing = Listing.objects.get(pk=listing_id)
    amount = float(form.get("offer"))

    if is_valid_bid(listing, amount):
        Bid.objects.create(listing=listing, user=request.user, amount=amount)
        listing.current_bid = amount
        listing.save()

        return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing.id}))
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "bid_error": True
        })


def is_valid_bid(listing, amount):
    if amount >= listing.starting_bid and ( listing.current_bid is None or amount > listing.current_bid):
        return True
    else:
        return False


@login_required
def close_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    listing.active = False
    listing.buyer = Bid.objects.filter(listing=listing).last().user
    listing.save()
    return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing.id}))


@login_required
def comment(request, listing_id):
    form = request.POST
    listing = Listing.objects.get(pk=listing_id)
    Comment.objects.create(listing=listing, author=request.user, message=form.get("message"))
    return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing.id}))


@login_required
def watchlist(request):
    listings = request.user.watched_listings.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


def category(request):
    form = request.GET

    # if category is less that 0, it means the user didnt pick a category then go back to index
    if int(form.get("category")) < 0:
        return HttpResponseRedirect(reverse('index'))
    else:
        listings = Listing.objects.filter(active=True, category=Category.objects.get(pk=int(form.get("category"))))
        return render(request, "auctions/category.html", {
            "categories": Category.objects.all(),
            "selected": Category.objects.get(pk=form.get("category")),
            "listings": listings
        })