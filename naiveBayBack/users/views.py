from django.shortcuts import render

# Create your views here.
from django.conf import settings
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from django.apps import apps
from .serializers import UserSerializer
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, ChangePasswordSerializer
from rest_framework.exceptions import ValidationError
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
    permission_classes = [IsAdminUser]


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
        username = self.request.query_params.get('username')
        
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
