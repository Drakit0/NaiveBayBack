from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from .models import Category, Auction, Bid, Rating
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from .serializers import (
    CategoryListCreateSerializer,
    CategoryDetailSerializer,
    AuctionListCreateSerializer,
    AuctionDetailSerializer,
    BidListCreateSerializer,
    BidDetailSerializer,
    RatingDetailSerializer,
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from .permissions import IsAuthenticatedAuction, IsAdminCategory, IsAuctioneerOrAdmin, IsRaterOrAdmin, IsBidderOrAdmin
from decimal import Decimal


class CategoryListCreate(generics.ListCreateAPIView):
    """
    List and create categories.
    List accessible to all users.
    Create accessible only to administrators.
    """

    queryset = Category.objects.all()
    serializer_class = CategoryListCreateSerializer
    permission_classes = [IsAdminCategory]


class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a category.
    Accessible only to administrators.
    """

    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer
    permission_classes = [IsAdminCategory]


class AuctionListCreate(generics.ListCreateAPIView):
    """
    List and create auctions.
    List accessible to all users.
    Create accessible only to authenticated users."""

    queryset = Auction.objects.all()
    serializer_class = AuctionListCreateSerializer
    permission_classes = [IsAuthenticatedAuction]

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        search = params.get("search")
        category = params.get("category")
        min_price = params.get("min_price")
        max_price = params.get("max_price")

        if search and len(search) < 3:
            raise ValidationError(
                {"search": "Search query must be at least 3 characters long."},
                code=status.HTTP_400_BAD_REQUEST,
            )

        if search:
            # Fix so description is considered too
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        if category:
            # TODO: see how I can make it so the category exists in the db
            queryset = queryset.filter(category__name__icontains=category)

        if min_price and max_price:
            if float(min_price) > float(max_price):
                raise ValidationError(
                    {
                        "min_price": "Minimum price cannot be greater than maximum price."
                    },
                    code=status.HTTP_400_BAD_REQUEST,
                )
            if float(min_price) < 0 or float(max_price) < 0:
                raise ValidationError(
                    {"price": "Price cannot be negative."},
                    code=status.HTTP_400_BAD_REQUEST,
                )
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset


class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an auction.
    Accessible only to administrators or the auctioneer.
    """

    queryset = Auction.objects.all()
    serializer_class = AuctionDetailSerializer
    permission_classes = [IsAuctioneerOrAdmin]


class BidListCreate(generics.ListCreateAPIView):
    """
    List and create bids.
    List accessible to all users.
    Create accessible only to authenticated users.
    """

    queryset = Bid.objects.all()
    serializer_class = BidListCreateSerializer

    # permission_classes = [IsAuthenticatedAuction]

    def get_queryset(self):
        auction = get_object_or_404(Auction, id=self.kwargs["auction_id"])
        return super().get_queryset().filter(auction=auction)

    def perform_create(self, serializer):
        auction_id = self.kwargs["auction_id"]
        auction = get_object_or_404(Auction, id=auction_id)
        user = self.request.data.get("user")
        price_str = self.request.data.get("price")
        price = Decimal(price_str) if price_str else None
        if auction.closing_date <= timezone.now():
            raise ValidationError({"price": "Cannot bid on closed auctions"})

        # Check if bid is highest
        highest_bid = Bid.objects.filter(auction=auction).first()

        if highest_bid and price <= highest_bid.price:
            raise ValidationError(
                {"price": f"Must exceed current highest bid ({highest_bid.price})"}
            )

        if not highest_bid and price < auction.price:
            raise ValidationError(
                {"price": f"Must meet starting price of {auction.price}"}
            )

        # serializer.save(auction_id=auction_id, bidder=self.request.user)
        serializer.save(auction_id=auction_id, bidder=self.request.user)


class BidRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a bid.
    Accessible only to administrators or the bidder.
    """

    queryset = Bid.objects.all()
    serializer_class = BidDetailSerializer
    lookup_url_kwarg = "pk"
    permission_classes = [IsAuthenticatedAuction]

    def get_queryset(self):
        bids = super().get_queryset()

        auction_id = self.kwargs.get("auction_id")
        # bid_id = self.kwargs.get("bid_pk")
        # Filter by both auction AND bid ID
        # return bids.filter(auction_id=auction_id, id=bid_id)
        return bids.filter(auction_id=auction_id)

    def perform_update(self, serializer):
        bid = self.get_object()
        auction = bid.auction
        price = serializer.validated_data.get("price")

        if auction.closing_date <= timezone.now():
            raise ValidationError({"price": "Cannot update bid on closed auctions"})

        highest_bid = Bid.objects.filter(auction=auction).exclude(id=bid.id).first()

        if highest_bid and price <= highest_bid.price:
            raise ValidationError(
                {"price": f"Must exceed current highest bid ({highest_bid.price})"}
            )

        if not highest_bid and price < auction.price:
            raise ValidationError(
                {"price": f"Must meet starting price of {auction.price}"}
            )

        serializer.save()

    def perform_destroy(self, instance):
        auction = instance.auction

        if auction.closing_date <= timezone.now():
            raise ValidationError({"detail": "Cannot delete bid on closed auctions"})

        instance.delete()


class UserAuctionListView(APIView):
    """
    View to list and edit auctions of the authenticated users.
    Accessible only to admin users.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        # Obtener las subastas del usuario autenticado
        user_auctions = Auction.objects.filter(auctioneer=request.user)
        serializer = AuctionListCreateSerializer(user_auctions, many=True)
        return Response(serializer.data)
    
class RatingRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a rating.
    Accessible only to administrators or the rater.
    """
    
    queryset = Rating.objects.all()
    serializer_class = RatingDetailSerializer
    permission_classes = [IsAuthenticated, IsRaterOrAdmin]
    
    def get_object(self):
        # fetch the auction (404 if bad ID)
        auction = get_object_or_404(Auction, pk=self.kwargs['auction_id'])
        # get the user’s Rating or create one with rating=1
        rating_obj, created = Rating.objects.get_or_create(
            auction=auction,
            user=self.request.user,
            defaults={'rating': 1},
        )
        return rating_obj
    
    def perform_update(self, serializer):
        rating = self.get_object()
        auction = rating.auction
        rating_value = serializer.validated_data.get("rating")
        
        if rating_value < 1 or rating_value > 5:
            raise ValidationError({"rating": "Rating must be between 1 and 5"})
        
        if auction.closing_date <= timezone.now():
            raise ValidationError({"detail": "Cannot update rating on closed auctions"})
        
        serializer.save()
        
    def perform_destroy(self, instance):
        auction = instance.auction

        if auction.closing_date <= timezone.now():
            raise ValidationError({"detail": "Cannot delete rating on closed auctions"})

        instance.delete()
