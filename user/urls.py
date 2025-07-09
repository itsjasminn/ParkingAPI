from django.urls import path
from rest_framework import routers

from user.views import (
    RegisterCreateAPIView,
    ForgotAPIView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    VerifyOTPAPIView,
    ChangePasswordAPIView, ProfileAPIView, ProfileUpdateAPIView, ProfileListAPIView, ProfileDestroyAPIView, UserViewSet)

router = routers.SimpleRouter()
router.register(r'users', UserViewSet)

# --------------------- AUTH --------------------
urlpatterns = [
    path("register", RegisterCreateAPIView.as_view()),
    path('login', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path("forgot-password", ForgotAPIView.as_view()),
    path("verify-otp", VerifyOTPAPIView.as_view()),
    path("change-password", ChangePasswordAPIView.as_view()),
]

# --------------------- profile --------------------
urlpatterns += [
    path("profile/about" , ProfileAPIView.as_view()),
    path("profile/update" , ProfileUpdateAPIView.as_view()),
    # path("profile/update" , ProfileUpdateAPIView.as_view()),
    path("profile/list" , ProfileListAPIView.as_view()),
    path("profile/<int:pk>" , ProfileDestroyAPIView.as_view()),
]

urlpatterns += router.urls

