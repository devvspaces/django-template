from django.urls import path

from .views import LoginView, LogoutView, RegisterView

app_name = 'auth'
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="signup"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
