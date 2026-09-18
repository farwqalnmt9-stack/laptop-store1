from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import RegisterForm


class StoreLoginView(LoginView):
    template_name = 'accounts/login.html'


class StoreLogoutView(LogoutView):
    next_page = 'store:home'


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('store:home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})
