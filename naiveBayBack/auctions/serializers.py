from rest_framework import serializers
from django.utils import timezone
from .models import Category, Auction, Bid
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

    @extend_schema_field(serializers.BooleanField())
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()

    def validate_closing_date(self, value):
        # TODO: make it so the closing 15 days after creation works
        if value <= timezone.now() + timedelta(days=15):
            raise serializers.ValidationError(
                "Closing date must be at least 15 days from now"
            )
        return value


class AuctionDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True
    )
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    isOpen = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Auction
        fields = "__all__"

    @extend_schema_field(serializers.BooleanField())
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()

    def validate_closing_date(self, value):
        if value <= timezone.now() + timedelta(days=15):
            raise serializers.ValidationError(
                "Closing date must be at least 15 days from now"
            )
        return value


class BidListCreateSerializer(serializers.ModelSerializer):
    # TODO: see what fields we should include for bids
    creation_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True
    )

    class Meta:
        model = Bid
        fields = "__all__"

    def validate(self, attrs):
        bid_value = attrs["bid_value"]
        auction = attrs["auction"]

        # Check if auction is open
        if auction.closing_date <= timezone.now():
            raise serializers.ValidationError(
                {"bid_value": "Cannot bid on closed auctions"}
            )

        # Check if bid is highest
        highest_bid = Bid.objects.filter(auction=auction).first()

        if highest_bid and bid_value <= highest_bid.bid_value:
            raise serializers.ValidationError(
                {
                    "bid_value": f"Must exceed current highest bid ({highest_bid.bid_value})"
                }
            )

        if not highest_bid and bid_value < auction.price:
            raise serializers.ValidationError(
                {"bid_value": f"Must meet starting price of {auction.price}"}
            )

        return attrs


class BidDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True
    )

    class Meta:
        model = Bid
        fields = "__all__"

    def validate(self, attrs):
        bid_value = attrs["bid_value"]
        auction = attrs["auction"]

        # Check if auction is open
        if auction.closing_date <= timezone.now():
            raise serializers.ValidationError(
                {"bid_value": "Cannot bid on closed auctions"}
            )

        # Check if bid is highest
        highest_bid = Bid.objects.filter(auction=auction).first()

        if highest_bid and bid_value <= highest_bid.bid_value:
            raise serializers.ValidationError(
                {
                    "bid_value": f"Must exceed current highest bid ({highest_bid.bid_value})"
                }
            )

        if not highest_bid and bid_value < auction.price:
            raise serializers.ValidationError(
                {"bid_value": f"Must meet starting price of {auction.price}"}
            )

        return attrs
