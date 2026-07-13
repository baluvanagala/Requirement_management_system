from django.urls import path
from .views import (
    EmailOrPhoneRegistrationView,
    VerifyOTPView,
    LoginView
)

urlpatterns = [
    path('register/', EmailOrPhoneRegistrationView.as_view(), name='email-register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
]
