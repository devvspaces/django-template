from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from django.contrib.auth import authenticate, login, logout

from authapp.forms import LoginForm, UserRegisterForm


class LoginView(FormView):
    template_name = "authapp/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            messages.success(self.request, "Login successful", extra_tags="success")
            login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        # Check if next is in the query string
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url
        return reverse("dashboard:home")


class RegisterView(FormView):
    template_name = "authapp/signup.html"
    form_class = UserRegisterForm

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Account created successfully, you can now login",
            extra_tags="success",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "Fill all the required fields accurately", extra_tags="danger"
        )
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("auth:login")


class LogoutView(TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Logout successful", extra_tags="success")
        return redirect("auth:login")
