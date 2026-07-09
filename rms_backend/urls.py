from django.urls import path
from rms_backend.views import Reset_password,Forget_password
urlpatterns = [
        path('Forget/',Forget_password.as_view()),
        path('reset_password/',Reset_password.as_view()),
        
]
