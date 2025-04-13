from django.urls import path
from .views import (
    UserListView,
    UserRetrieveUpdateDestroyView,
    LogoutView,
    UserProfileView,
    ChangePasswordView,
    UserAuctionsListView,
    UserBidsListView,
)

app_name = "users"
urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserRetrieveUpdateDestroyView.as_view(), name="user-detail"),
    path("profile/", UserProfileView.as_view(), name="user-profile-username"),
    path("profile/<str:username>/", UserProfileView.as_view(), name="user-profile-username"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("log-out/", LogoutView.as_view(), name="log-out"),
    path("myAuctions/", UserAuctionsListView.as_view(), name="user-auctions"),
    path("myBids/", UserBidsListView.as_view(), name="user-bids"),
]
