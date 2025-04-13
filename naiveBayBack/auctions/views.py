from django.shortcuts import render
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


class BidListCreate(generics.ListCreateAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidListCreateSerializer


class BidRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidDetailSerializer
