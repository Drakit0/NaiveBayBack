from rest_framework import serializers
from .models import CustomUser
from auctions.models import Auction, Bid, Rating, Comment
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            # "is_staff",
            "id",
            "username",
            "email",
            "birth_date",
            "municipality",
            "locality",
            "password",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_email(self, value):
        user = self.instance  # Solo tiene valor cuando se está actualizando
        if (
            CustomUser.objects.filter(email=value)
            .exclude(pk=user.pk if user else None)
            .exists()
        ):
            raise serializers.ValidationError("Email already in used.")
        return value

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
class MyAuctionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = (
            "id",
            "title",
            "description",
            "price",
            "avg_rating",
            "stock",
            "brand",
            "category",
            "thumbnail",
            "image",
            "creation_date",
            "closing_date",
            # "auctioneer",
        )
        
        read_only_fields = (
            "id",
            "title",
            "description",
            "price",
            "avg_rating",
            "stock",
            "brand",
            "category",
            "thumbnail",
            "image",
            "creation_date",
            "closing_date",
            # "auctioneer",
        )


class MyBidsSerializer(serializers.ModelSerializer):
    auction = serializers.StringRelatedField(read_only=True)
    # bidder = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Bid
        fields = (
            "id",
            "price",
            "auction",
            # "bidder",
            "creation_date",
        )
        read_only_fields = (
            "id",
            "auction",
            # "bidder",
            "creation_date",
        )
        
class MyRatingsSerializer(serializers.ModelSerializer):
    
    auction_title = serializers.CharField(source="auction.title", read_only=True)
    auction_price = serializers.DecimalField(
        source="auction.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    auction_category = serializers.CharField(
        source="auction.category.name",
        read_only=True
    )
    is_open = serializers.SerializerMethodField(read_only=True)
    
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Rating
        fields = (
            "user",
            "auction_title",
            "auction_price",
            "auction_category",
            "is_open",
            "rating",
        )
        read_only_fields = (
            "user",
            "auction_title",
            "auction_price",
            "auction_category",
            "is_open",
            "rating",
        )

    def get_is_open(self, obj):
        return obj.auction.closing_date > timezone.now()
    
class MyCommentsSerializer(serializers.ModelSerializer):
    
    auction_title = serializers.CharField(source="auction.title", read_only=True)
    auction_price = serializers.DecimalField(
        source="auction.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    auction_category = serializers.CharField(
        source="auction.category.name",
        read_only=True
    )
    is_open = serializers.SerializerMethodField(read_only=True)
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = (
            "user",
            "auction_title",
            "auction_price",
            "auction_category",
            "is_open",
            "title",
            "content",
        )
        read_only_fields = (
            "user",
            "auction_title",
            "auction_price",
            "auction_category",
            "is_open",
            "title",
            "content",
        )

    def get_is_open(self, obj):
        return obj.auction.closing_date > timezone.now()
