from django.urls import path
from .views import ForgotPassword, ResetPassword

urlpatterns = [

    path("Forgot/",ForgotPassword.as_view()),
    path("reset-password/<uidb64>/<token>/",ResetPassword.as_view()),

]