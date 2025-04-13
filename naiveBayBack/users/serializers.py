from rest_framework import serializers
from .models import CustomUser
from auctions.models import Auction, Bid


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
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
            "rating",
            "stock",
            "brand",
            "category",
            "thumbnail",
            "creation_date",
            "closing_date",
            "auctioneer",
        )
        read_only_fields = (
            "id",
            "title",
            "description",
            "price",
            "rating",
            "stock",
            "brand",
            "category",
            "thumbnail",
            "creation_date",
            "closing_date",
            "auctioneer",
        )


class MyBidsSerializer(serializers.ModelSerializer):
    auction = serializers.StringRelatedField(read_only=True)
    bidder = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Bid
        fields = (
            "id",
            "price",
            "auction",
            "bidder",
            "creation_date",
        )
        read_only_fields = (
            "id",
            "auction",
            "bidder",
            "creation_date",
        )
