from django.urls import path
from .views import LoginView, LogoutView, UserAPIView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', UserAPIView.as_view()),
    path('users/<int:pk>/', UserAPIView.as_view()),
]

