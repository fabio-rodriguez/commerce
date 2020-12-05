from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='listings', default=None, blank=True, null=True)
    users_watchlists = models.ManyToManyField(User, blank=True, related_name='watchlist')
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1024)
    img_url = models.CharField(max_length=256)
    initial_bid = models.DecimalField(max_digits=8, decimal_places=2)
    active = models.BooleanField(max_length=1)
    date_creation = models.DateTimeField(auto_now_add=True)
    auction_winner_id = models.IntegerField(blank=True, default=0)

    def current_bid(self):
        return self.initial_bid if not self.bids.count() else self.bids.order_by('value').last().value   

    def winner(self):
        return self.bids.order_by('value').last().user

    def is_on_watchlist(self, user):
        if self.users_watchlists.count() and self.users_watchlists.filter(pk=user.id):
            return True    
        else:
            return False    

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    value = models.DecimalField(max_digits=8, decimal_places=2)
    date_creation = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    text = models.CharField(max_length=1024)
    date_creation = models.DateTimeField(auto_now_add=True)
