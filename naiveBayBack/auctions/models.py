from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser
from decimal import Decimal


class Category(models.Model):

    name = models.CharField(max_length=50, blank=False, unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


class Auction(models.Model):

    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )
    # rating = models.DecimalField(max_digits=3, decimal_places=2)
    stock = models.IntegerField(validators=[MinValueValidator(1)])
    brand = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category, related_name="auctions", on_delete=models.CASCADE
    )

    thumbnail = models.URLField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to="thumbnails/")

    creation_date = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateTimeField()
    auctioneer = models.ForeignKey(
        CustomUser, related_name="auctions", on_delete=models.CASCADE
    )

    @property
    def avg_rating(self):
        agg = self.ratings.aggregate(avg=models.Avg("rating"))

        return round(agg["avg"] or 1.0, 2)

    @property
    def image_url(self):
        if self.thumbnail:
            return self.thumbnail

        if self.image:
            return self.image.url

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.title


class Bid(models.Model):

    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    auction = models.ForeignKey(Auction, related_name="bids", on_delete=models.CASCADE)
    bidder = models.ForeignKey(
        CustomUser, related_name="bids", on_delete=models.CASCADE
    )
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-price",)

    def __str__(self):
        return f"{self.id}-{self.price}"


class Rating(models.Model):

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    auction = models.ForeignKey(
        Auction, related_name="ratings", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        CustomUser, related_name="ratings", on_delete=models.CASCADE
    )
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-rating",)
        unique_together = ("user", "auction")

    def __str__(self):
        return f"{self.user},{self.auction}-{self.rating}"


class Comment(models.Model):

    title = models.CharField(max_length=500)
    content = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        CustomUser, related_name="comments", on_delete=models.CASCADE
    )
    auction = models.ForeignKey(
        Auction, related_name="comments", on_delete=models.CASCADE
    )
    id = models.AutoField(primary_key=True)

    class Meta:
        ordering = ("-creation_date",)

    def __str__(self):
        return f"{self.user_id} - {self.auction_id} - {self.title} "
