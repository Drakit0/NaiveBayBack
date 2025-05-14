from django.shortcuts import render

# Create your views here.
from django.conf import settings
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from django.apps import apps
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserSerializer,
    ChangePasswordSerializer,
    MyAuctionsSerializer,
    MyBidsSerializer,
    MyRatingsSerializer,
    MyCommentsSerializer,
)
from auctions.models import Auction, Bid, Rating, Comment
from .models import CustomUser
from rest_framework.exceptions import ValidationError, NotFound
from django.contrib.auth.password_validation import validate_password
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .permissions import IsNotRegistered, IsOwnerOrAdmin



class UserRegisterView(generics.CreateAPIView):
    """
    View to register a new user.
    Allows creating a new user and returns the access token.
    Accessible only to unregistered users.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsNotRegistered]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "user": serializer.data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    """
    View to list all users.
    Accessible only to administrators.
    """

    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    # permission_classes = [IsAdminUser]


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a specific user.
    Accessible only to administrators or the user themselves.
    """

    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsOwnerOrAdmin]


class LogoutView(APIView):
    """
    View to perform user logout.
    Revokes the user's RefreshToken.
    Accessible only to authenticated users.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Realiza el logout eliminando el RefreshToken (revocar)"""
        try:
            # Obtenemos el RefreshToken del request
            # Se esperan que esté en el header Authorization
            refresh_token = request.data.get("refresh", None)
            if not refresh_token:
                return Response(
                    {"detail": "No refresh token provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Revocar el RefreshToken
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self):
        username = self.request.query_params.get("username")

        if username:
            if self.request.user.is_staff:
                UserModel = apps.get_model(settings.AUTH_USER_MODEL)
                try:
                    return UserModel.objects.get(username=username)

                except UserModel.DoesNotExist:
                    raise ValidationError({"detail": "User not found."})

            # Non-staff may only query their own profile.
            if self.request.user.username == username:
                return CustomUser.objects.get(id=self.request.user.id)

            self.permission_denied(self.request)

        return self.request.user

    def get(self, request):
        user = self.get_object()
        self.check_object_permissions(request, user)
        serializer = UserSerializer(user)

        return Response(serializer.data)

    def patch(self, request):
        user = self.get_object()
        self.check_object_permissions(request, user)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = self.get_object()
        self.check_object_permissions(request, user)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    """
    View to change the password of the authenticated user.
    Accessible only to the user themselves.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        user = request.user
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response(
                    {"old_password": "Incorrect current password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                validate_password(serializer.validated_data["new_password"], user)
            except ValidationError as e:
                return Response(
                    {"new_password": e.messages}, status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"detail": "Password updated successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAuctionsListView(generics.ListAPIView):
    """
    View to list all auctions of a specific user.
    Accessible only to the user themselves or an administrator.
    """
    
    serializer_class = MyAuctionsSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        request = self.request

        if request.user.is_staff:
            # Admins can view auctions of any user
            user_pk = request.query_params.get("user")
            
            if not user_pk:
                raise NotFound(detail="Missing required query parameter: user")
            
            try:
                target = CustomUser.objects.get(pk=user_pk)
                
            except CustomUser.DoesNotExist:
                raise NotFound(detail=f"No user with id={user_pk}")
            
        else:
            # Regular users can only view their own auctions
            target = request.user

        # related_name="auctions" on Auction.auctioneer
        return target.auctions.all()


class UserBidsListView(generics.ListAPIView):
    """
    View to list all bids of a specific user.
    Accessible only to the user themselves or an administrator.
    """
    
    serializer_class = MyBidsSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        request = self.request

        if request.user.is_staff:
            # Admins can view bids of any user
            user_pk = request.query_params.get("user")
            
            if not user_pk:
                raise NotFound(detail="Missing required query parameter: user")
            
            try:
                target = CustomUser.objects.get(pk=user_pk)
                
            except CustomUser.DoesNotExist:
                raise NotFound(detail=f"No user with id={user_pk}")
            
        else:
            # Regular users can only view their own bids
            target = request.user

        # related_name="bids" on Bid.bidder
        return target.bids.all()


class UserRatingsListView(generics.ListAPIView):
    """
    View to list all ratings of a specific user or all users if admin.
    Accessible only to the user themselves or an administrator.
    """
    
    serializer_class = MyRatingsSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        request = self.request

        if request.user.is_staff:
            # Admins can view ratings of any user or all users
            user_pk = request.query_params.get("user")
            
            if user_pk:
                try:
                    target = CustomUser.objects.get(pk=user_pk)
                    return target.ratings.all()
                except CustomUser.DoesNotExist:
                    raise NotFound(detail=f"No user with id={user_pk}")
            else:
                # Return all ratings if no specific user is provided
                return Rating.objects.all()
            
        else:
            # Regular users can only view their own ratings
            target = request.user

        # related_name="ratings" on Rating.user
        return target.ratings.all()


class UserCommentsListView(generics.ListAPIView):
    """
    View to list all comments of a specific user or all users if admin.
    Accessible only to the user themselves or an administrator.
    """
    
    serializer_class = MyCommentsSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        request = self.request

        if request.user.is_staff:
            # Admins can view comments of any user or all users
            user_pk = request.query_params.get("user")
            
            if user_pk:
                try:
                    target = CustomUser.objects.get(pk=user_pk)
                    return target.comments.all()
                except CustomUser.DoesNotExist:
                    raise NotFound(detail=f"No user with id={user_pk}")
            else:
                # Return all comments if no specific user is provided
                return Comment.objects.all()
            
        else:
            # Regular users can only view their own comments
            target = request.user

        # related_name="comments" on Comment.user
        return target.comments.all()