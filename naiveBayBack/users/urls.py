from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import (
    UserListView,
    UserRetrieveUpdateDestroyView,
    LogoutView,
    UserProfileView,
    ChangePasswordView,
    UserAuctionsListView,
    UserBidsListView,
    UserRegisterView,
    UserRatingsListView,
    UserCommentsListView,
)
from rest_framework_simplejwt.views import TokenObtainPairView

app_name = "users"
urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login-user"),
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserRetrieveUpdateDestroyView.as_view(), name="user-detail"),
    path("profile/", UserProfileView.as_view(), name="user-profile-username"),
    path(
        "profile/<str:username>/",
        UserProfileView.as_view(),
        name="user-profile-username",
    ),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("log-out/", LogoutView.as_view(), name="log-out"),
    path("myAuctions/", UserAuctionsListView.as_view(), name="user-auctions"),
    path("myBids/", UserBidsListView.as_view(), name="user-bids"),
    path("myRatings/", UserRatingsListView.as_view(), name="user-ratings"),
    path("myComments/", UserCommentsListView.as_view(), name="user-comments"),
    
    path("register/", UserRegisterView.as_view(), name="user-register"),

    
]
