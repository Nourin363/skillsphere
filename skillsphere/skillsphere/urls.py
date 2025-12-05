"""
URL configuration for skillsphere project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from app import views
from app.views import dashboard, skill_data



urlpatterns = [
    path('admin/', admin.site.urls),
    path('adminpanel/', include('adminpanel.urls')),
    # path('', include('app.urls')),

    # ---------------- 🌐 PUBLIC ----------------
    path('', views.index, name='index'),

    # ---------------- 🔐 AUTHENTICATION ----------------
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # ---------------- 👤 USER AREA ----------------
    path('dashboard/', views.dashboard, name='dashboard'),
    path("skills/data/", skill_data, name="skill_data"),

    path('skills/', views.skills, name='skills'),
    path('skills/practice/<slug:slug>/', views.skill_practice, name='skill_practice'),
    path('skills/add/', views.add_skill, name='add_skill'),
    path('skills/<int:skill_id>/edit/', views.edit_skill, name='edit_skill'),
    path('skills/<int:skill_id>/delete/', views.delete_skill, name='delete_skill'),
    path('skills/progress/', views.skill_progress, name='skill_progress'),
    path('skill/<int:skill_id>/', views.skill_detail, name='skill_detail'),
    path('skill/<slug:skill_slug>/task/<int:task_id>/', views.task_detail, name='task_detail'),
    path("skill/<slug:skill_slug>/hub/<str:difficulty>/", views.skill_hub, name="skill_hub"),
    path('skill/<slug:skill_slug>/quiz/', views.skill_quiz, name='skill_quiz'),





    path("skills/<slug:slug>/task/<int:task_id>/open/", views.task_open, name="task_open"),
    path("skills/complete/", views.complete_task, name="complete_task"),

    path('internships/', views.internships, name='internships'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),


    # 📨 Internship Application (new)
    path('apply_internship/', views.apply_internship, name='apply_internship'),

    # ---------------- 🔑 PASSWORD RESET FLOW ----------------
    # Step 1: Request reset
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(template_name='password_reset.html'),
        name='password_reset'
    ),

    # Step 2: Email sent confirmation
    path(
        'password_reset_done/',
        auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'
    ),

    # Step 3: Reset link confirmation (via email)
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'
    ),

    # Step 4: Completion message
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        name='password_reset_complete'
    ),
    
]
