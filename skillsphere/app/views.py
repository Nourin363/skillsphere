from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Profile, Skill, UserSkill, MicroInternship

# --------------------------- PUBLIC ---------------------------

def index(request):
    """Home page."""
    return render(request, 'index.html')


# --------------------------- AUTH ---------------------------

def register_view(request):
    """User registration."""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        Profile.objects.create(user=user)  # Auto create profile
        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    """User login."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials.')

    return render(request, 'login.html')


def logout_view(request):
    """Logout user."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# --------------------------- USER AREA ---------------------------

def dashboard(request):
    """Dashboard with quick stats."""
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'dashboard.html')


def skills(request):
    """Skill tracking page."""
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'skills.html')


def internships(request):
    """Micro-Internships list page."""
    if not request.user.is_authenticated:
        return redirect('login')

    internships = MicroInternship.objects.all()
    return render(request, 'internships.html', {'internships': internships})


def profile(request):
    """Profile page."""
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'profile.html')
