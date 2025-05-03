from rest_framework import serializers
from django.utils import timezone
from .models import Category, Auction, Bid, Rating, Comment
from drf_spectacular.utils import extend_schema_field
from datetime import timedelta


class CategoryListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class AuctionListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True
    )
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    isOpen = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Auction
        fields = "__all__"
        read_only_fields = ("auctioneer", "creation_date", "avg_rating")

    @extend_schema_field(serializers.BooleanField())
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()
    
    def get_avg_rating(self, obj):
        return obj.avg_rating

    def validate_closing_date(self, value):
        # TODO: make it so the closing 15 days after creation works
        if value <= timezone.now() + timedelta(days=15):
            raise serializers.ValidationError(
                "Closing date must be at least 15 days from now"
            )
        return value

    def create(self, validated_data):
        # Set auctioneer to the user from the request, overriding any client input.
        validated_data["auctioneer"] = self.context["request"].user
        return super().create(validated_data)


class AuctionDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True
    )
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    isOpen = serializers.SerializerMethodField(read_only=True)
    avg_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Auction
        fields = "__all__"
        read_only_fields = ("auctioneer", "creation_date", "avg_rating")

    @extend_schema_field(serializers.BooleanField())
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()
    
    def get_avg_rating(self, obj):
        return obj.avg_rating

    def validate_closing_date(self, value):
        if value <= timezone.now() + timedelta(days=15):
            raise serializers.ValidationError(
                "Closing date must be at least 15 days from now"
            )
        return value

    def create(self, validated_data):
        # Set auctioneer to the user from the request, overriding any client input.
        validated_data["auctioneer"] = self.context["request"].user
        return super().create(validated_data)


class BidListCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bid
        fields = (
            "id",
            "price",
            "bidder",
            # "auction",
        )
        read_only_fields = ("bidder",)


class BidDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True
    )

    class Meta:
        model = Bid
        fields = "__all__"

        read_only_fields = (
            "bidder",
            "auction",
        )

    # def validate(self, attrs):
    #     price = attrs["price"]
    #     auction = attrs["auction"]

    #     # Check if auction is open
    #     if auction.closing_date <= timezone.now():
    #         raise serializers.ValidationError(
    #             {"price": "Cannot bid on closed auctions"}
    #         )

    #     # Check if bid is highest
    #     highest_bid = Bid.objects.filter(auction=auction).first()

    #     if highest_bid and price <= highest_bid.price:
    #         raise serializers.ValidationError(
    #             {"price": f"Must exceed current highest bid ({highest_bid.price})"}
    #         )

    #     if not highest_bid and price < auction.price:
    #         raise serializers.ValidationError(
    #             {"price": f"Must meet starting price of {auction.price}"}
    #         )

    #     return attrs
    
class RatingDetailSerializer(serializers.ModelSerializer):
    
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    
    class Meta:
        model = Rating
        fields = "__all__"
        read_only_fields = ("user", "auction")
        
class CommentDetailSerializer(serializers.ModelSerializer):
    
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    edit_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    
    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ("id","user", "auction", "creation_date", "edit_date")
        
class CommentListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "title", "content", "creation_date", "edit_date"]
        read_only_fields = ["id","creation_date", "edit_date"]
