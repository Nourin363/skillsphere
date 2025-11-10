from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile, Skill, UserSkill, MicroInternship, Application


# --------------------------- 🌐 PUBLIC ---------------------------

def index(request):
    """Home page."""
    return render(request, 'index.html')


# --------------------------- 🔐 AUTH ---------------------------

def register_view(request):
    """User registration with auto login."""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validation
        if not all([first_name, last_name, username, email, password1, password2]):
            messages.error(request, "All fields are required.")
            return redirect('register')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        Profile.objects.create(user=user)

        # Auto-login
        login(request, user)
        messages.success(request, f"Welcome to SkillSphere, {first_name}! 🎉")
        return redirect('dashboard')

    return render(request, 'register.html')


def login_view(request):
    """User login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return redirect('login')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}! 👋")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'login.html')


def logout_view(request):
    """Logout user."""
    logout(request)
    messages.info(request, "👋 You have been logged out successfully.")
    return redirect('login')


# --------------------------- 👤 USER AREA ---------------------------

@login_required(login_url='login')
def dashboard(request):
    """Dashboard with stats and dynamic skills."""
    total_skills = UserSkill.objects.filter(user=request.user).count()
    total_internships = MicroInternship.objects.count()
    total_applications = Application.objects.filter(user=request.user).count()
    user_skills = UserSkill.objects.filter(user=request.user).select_related('skill')

    context = {
        'total_skills': total_skills,
        'total_internships': total_internships,
        'total_applications': total_applications,
        'user_skills': user_skills,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def skills(request):
    """Display user's skills."""
    user_skills = UserSkill.objects.filter(user=request.user)
    return render(request, 'skills.html', {'user_skills': user_skills})


@login_required(login_url='login')
def add_skill(request):
    """Add a new skill (POST endpoint)."""
    if request.method == 'POST':
        skill_name = request.POST.get('skill_name')
        category = request.POST.get('category', 'General')
        progress = request.POST.get('progress', 0)

        if not skill_name:
            messages.error(request, "Skill name cannot be empty.")
            return redirect('skills')

        skill, created = Skill.objects.get_or_create(name=skill_name, category=category)
        UserSkill.objects.create(user=request.user, skill=skill, progress=progress)

        messages.success(request, f"✅ '{skill_name}' added successfully!")
        return redirect('skills')

    return redirect('skills')

@login_required(login_url='login')
def edit_skill(request, skill_id):
    """Edit a user's existing skill."""
    user_skill = get_object_or_404(UserSkill, id=skill_id, user=request.user)

    if request.method == 'POST':
        skill_name = request.POST.get('skill_name')
        category = request.POST.get('category', user_skill.skill.category)
        progress = request.POST.get('progress', user_skill.progress)

        # Update or create new Skill entry
        skill, _ = Skill.objects.get_or_create(name=skill_name, category=category)
        user_skill.skill = skill
        user_skill.progress = progress
        user_skill.save()

        messages.success(request, f"✅ '{skill_name}' updated successfully!")
        return redirect('skills')

    return redirect('skills')


@login_required(login_url='login')
def delete_skill(request, skill_id):
    """Delete a user's skill."""
    user_skill = get_object_or_404(UserSkill, id=skill_id, user=request.user)
    
    if request.method == 'POST':
        skill_name = user_skill.skill.name
        user_skill.delete()
        messages.success(request, f"🗑️ '{skill_name}' has been deleted successfully.")
        return redirect('skills')

    messages.error(request, "Something went wrong while deleting.")
    return redirect('skills')



@login_required(login_url='login')
def internships(request):
    """Micro-Internships list page."""
    internships = MicroInternship.objects.all().order_by('-id')
    return render(request, 'internships.html', {'internships': internships})


@login_required(login_url='login')
def apply_internship(request):
    """Handle internship applications."""
    if request.method == 'POST':
        internship_id = request.POST.get('internship_id')
        motivation = request.POST.get('motivation', '')

        internship = get_object_or_404(MicroInternship, id=internship_id)

        if Application.objects.filter(user=request.user, internship=internship).exists():
            messages.warning(request, "⚠️ You’ve already applied for this internship.")
            return redirect('internships')

        Application.objects.create(
            user=request.user,
            internship=internship,
            motivation=motivation,
            status='Pending'
        )

        messages.success(request, "✅ Application submitted successfully!")
        return redirect('internships')

    return redirect('internships')


@login_required
def profile(request):
    """User Profile Page with stats."""
    profile = get_object_or_404(Profile, user=request.user)

    user_skills = UserSkill.objects.filter(user=request.user)
    total_skills = user_skills.count()

    applications = Application.objects.filter(user=request.user)
    total_internships = applications.count()

    # Calculate average skill progress
    avg_progress = 0
    if total_skills > 0:
        avg_progress = int(sum(s.progress for s in user_skills) / total_skills)

    context = {
        'profile': profile,
        'total_skills': total_skills,
        'total_internships': total_internships,
        'avg_progress': avg_progress,
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    """Edit profile details for the logged-in user."""
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        messages.success(request, "✅ Profile updated successfully!")
        return redirect('profile')

    return render(request, 'edit_profile.html', {'profile': profile})

