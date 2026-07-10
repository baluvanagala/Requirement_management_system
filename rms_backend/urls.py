from django.urls import path
from rms_backend.views import Forgot,Reset_password,Change_password
from rest_framework_simplejwt.views import TokenObtainPairView
urlpatterns = [
    path("Forgot/",Forgot.as_view()),
    path("reset-password/<uidb64>/<token>/",Reset_password.as_view()),
    path("change_password/",Change_password.as_view()),
    path("login/", TokenObtainPairView.as_view()),
] 