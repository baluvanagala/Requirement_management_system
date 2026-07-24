from django.urls import path

from .views import LoginView, LogoutView, UserAPIView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', UserAPIView.as_view()),
    path('users/<int:pk>/', UserAPIView.as_view()),
]

# from .views import (
#     EmailOrPhoneRegistrationView,
#     VerifyOTPView,
#     LoginView
# )

# urlpatterns = [
#     path('register/', EmailOrPhoneRegistrationView.as_view(), name='email-register'),
#     path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
#     path('login/', LoginView.as_view(), name='login'),
# ]
# >>>>>>> register_api
