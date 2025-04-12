from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from .models import Category, Auction, Bid
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from .serializers import (
    CategoryListCreateSerializer,
    CategoryDetailSerializer,
    AuctionListCreateSerializer,
    AuctionDetailSerializer,
    BidListCreateSerializer,
    BidDetailSerializer,
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from .permissions import IsOwnerOrAdmin
from decimal import Decimal


class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListCreateSerializer


class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer


class AuctionListCreate(generics.ListCreateAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionListCreateSerializer

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
    queryset = Auction.objects.all()
    serializer_class = AuctionDetailSerializer
    permission_classes = [IsOwnerOrAdmin]


class BidListCreate(generics.ListCreateAPIView):
    # TODO: see how to add user
    queryset = Bid.objects.all()
    serializer_class = BidListCreateSerializer
    # permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        auction = get_object_or_404(Auction, id=self.kwargs["pk"])
        return super().get_queryset().filter(auction=auction)

    def perform_create(self, serializer):
        auction_id = self.kwargs["pk"]
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
        serializer.save(
            auction_id=auction_id,
        )


class BidRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidDetailSerializer
    lookup_url_kwarg = "bid_pk"

    def get_queryset(self):
        bids = super().get_queryset()

        auction_id = self.kwargs.get("pk")
        # bid_id = self.kwargs.get("bid_pk")
        # Filter by both auction AND bid ID
        # return bids.filter(auction_id=auction_id, id=bid_id)
        return bids.filter(auction_id=auction_id)


class UserAuctionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Obtener las subastas del usuario autenticado
        user_auctions = Auction.objects.filter(auctioneer=request.user)
        serializer = AuctionListCreateSerializer(user_auctions, many=True)
        return Response(serializer.data)
