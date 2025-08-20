from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('/')  # or your homepage
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'accounts/login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, "Passwords don't match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, "Account created. Please login.")
            return redirect('login')

    return render(request, 'accounts/register.html')


def logout_view(request):
    logout(request)
    return redirect('login')
