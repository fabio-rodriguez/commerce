from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


from .models import *

class CreateListingForm(forms.Form):
    title = forms.CharField(label="Title")
    description = forms.CharField(label="Description", widget=forms.Textarea())
    initial_bid = forms.DecimalField(label="Initial Bid", decimal_places=2, max_digits=8, min_value=0)
    img_url = forms.CharField(label="Image", max_length=256, required=False)
    active = forms.BooleanField(label="Active", required=False)


class PlaceBidForm(forms.Form):
    new_bid = forms.DecimalField(label="Place Bid", decimal_places=2, max_digits=8, min_value=0)


class AddCommentForm(forms.Form):
    text = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Add your comment", 'style' : 'width:100%'}))


def index(request):
    return render(request, "auctions/index.html", {
        "listings" : Listing.objects.exclude(active=False).all()
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
        form = CreateListingForm(request.POST)
        if form.is_valid():
            listing = Listing(user=request.user, title=form.cleaned_data["title"], img_url= form.cleaned_data["img_url"], 
                        description=form.cleaned_data["description"], initial_bid=form.cleaned_data["initial_bid"], 
                        active=form.cleaned_data["active"])
            try:
                listing.category = Category.objects.get(pk=request.POST["category"])
            except:
                pass
            listing.save()
        else:
            return render(request, "auctions/create.html", {
                "form": form,
                "categories": Category.objects.all()
            })
        
        return HttpResponseRedirect(reverse("listing", args=[listing.id]))    

    #If user is logged
    return render(request, "auctions/create.html", {
        "form": CreateListingForm(),
        "categories": Category.objects.all()
    })


def show(request, id_listing):            
    
    try:
        listing = Listing.objects.get(pk=id_listing) 
    except:
        return error_page(request, "Error, listing does not exists")

    if request.method == 'POST':
        if request.user.is_authenticated:
            if 'bid' in request.POST:
                return bid_post(request, listing)      
            elif 'watchlist' in request.POST:
                return watchlist_post(request, listing)
            elif 'close_listing' in request.POST:
                return close_listing_post(request, listing)
            elif 'add_comment' in request.POST:
                return add_comment_post(request, listing)
            else:
                return HttpResponse("ERROR: Page doesn't exists")            
        else:
            return HttpResponseRedirect(reverse('login'))

    return render_show_page(request, listing, PlaceBidForm(), AddCommentForm())


def render_show_page(request, listing, bid_form, comment_form):
    return render(request, 'auctions/show.html',{
        'listing': listing,
        'bids': listing.bids.order_by('value').all(),
        'on_watchlist': listing.is_on_watchlist(request.user),
        'bid_form': bid_form,
        'comment_form': comment_form,
        'comments': Comment.objects.filter(listing=listing).order_by('date_creation').all()
    })


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories" : Category.objects.all()
    })


@login_required
def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "listings" : request.user.watchlist.all()
    })


def category(request, id):
    return render(request, "auctions/category.html", {
        "category" : Category.objects.get(pk=id),
        "active_listings": bool([True for l in Category.objects.get(pk=id).listings.all() if l.active])
    })


def bid_post(request, listing):
    form = PlaceBidForm(request.POST)
    
    if form.is_valid():
        new_bid = form.cleaned_data["new_bid"]
        if (not listing.bids.count() and new_bid < listing.initial_bid) or (listing.bids.count() and new_bid <= listing.current_bid()):
            form.add_error("new_bid", "Your bid must be greater than current bid")
        else:
            bid = Bid(user=request.user, listing=listing, value=new_bid)
            bid.save()
            return HttpResponseRedirect(reverse("listing", args=[listing.id]))
    
    return render_show_page(request, listing, form, AddCommentForm()) 


def watchlist_post(request, listing):
    if int(request.POST['watchlist']):
        listing.users_watchlists.add(request.user)
    else:    
        listing.users_watchlists.remove(request.user)
    
    listing.save()
    return HttpResponseRedirect(reverse("listing", args=[listing.id]))


def close_listing_post(request, listing):
    
    if request.user == listing.user:
        listing.active = False
        if listing.bids.count(): 
            listing.auction_winner_id = listing.winner().id
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=[listing.id]))

    else:
        return HttpResponse("ERROR: You're not aloud to made this action.")


@login_required
def add_comment_post(request, listing):
    
    form = AddCommentForm(request.POST)

    if form.is_valid():
        text = form.cleaned_data["text"]
        comment = Comment(user=request.user, listing=listing, text=text)
        comment.save()
        return HttpResponseRedirect(reverse("listing", args=[listing.id]))

    return render_show_page(request, listing, PlaceBidForm(), form) 


def error_page(request, text):
    
    return render(request, "auctions/error.html", {
                "message": text,
            })
