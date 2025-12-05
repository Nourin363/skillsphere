import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from .models import User, Skill, UserSkill, SkillMaterial, PracticeQuestion, UserTask, MicroInternship, Application, Profile, Achievement, UserAchievement
from django.views.decorators.http import require_POST
from math import ceil
from .models import Notification
from app.models import LoginLog
from django.utils import timezone
from django.contrib.auth import logout
import math

def get_client_ip(request):
    x = request.META.get('HTTP_X_FORWARDED_FOR')
    if x:
        return x.split(',')[0]
    return request.META.get('REMOTE_ADDR', '')


# Public
def index(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')    # Admin → Admin Dashboard
        else:
            return redirect('dashboard')     # Normal User → User Dashboard
    return render(request, "index.html")      # Guest → Homepage


# Auth
def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

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

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        Profile.objects.create(user=user)
        login(request, user)
        messages.success(request, f"Welcome to SkillSphere, {first_name}! 🎉")
        return redirect('dashboard')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or request.GET.get('next')

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return redirect('login')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}! 👋")

            # 🔥 LOG LOGIN HERE
            LoginLog.objects.create(
                user=user,
                ip_address=get_client_ip(request),
                login_time=timezone.now()
            )

            # 🔥 Case 1: redirect to previous page if exists
            if next_url:
                return redirect(next_url)

            # 🔥 Case 2: otherwise dashboard based on role
            if user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')

        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'login.html')


def logout_view(request):
    # Track logout time & duration
    if request.user.is_authenticated:
        latest_log = LoginLog.objects.filter(
            user=request.user,
            logout_time__isnull=True
        ).order_by('-login_time').first()

        if latest_log:
            latest_log.logout_time = timezone.now()
            latest_log.session_duration = latest_log.logout_time - latest_log.login_time
            latest_log.save()
    logout(request)
    messages.info(request, "👋 You have been logged out successfully.")
    return redirect('index')


# Dashboard & JSON endpoint
@login_required(login_url='login')
def dashboard(request):
    user = request.user

    # Existing data
    user_skills = UserSkill.objects.filter(user=user).select_related('skill').order_by('-updated_at')
    skills_count = user_skills.count()
    internships_count = MicroInternship.objects.count()
    applications_count = Application.objects.filter(user=user).count()

    avg_progress = 0
    if skills_count:
        avg_progress = int(sum(us.progress for us in user_skills) / skills_count)

    # 🔔 Notifications
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    total_skills = user_skills.count()
    total_internships = MicroInternship.objects.count()
    total_applications = Application.objects.filter(user=user).count()
    context = {
        'total_skills': total_skills,
        'total_internships': total_internships,
        'total_applications': total_applications,
        'user_skills': user_skills,
        'skills_count': skills_count,
        'internships_count': internships_count,
        'applications_count': applications_count,
        'avg_progress': avg_progress,

        # added
        'notifications': notifications,
        'unread_count': unread_count,
    }

    return render(request, 'dashboard.html', context)



@login_required(login_url='login')
def skill_data(request):
    user_skills = UserSkill.objects.filter(user=request.user).select_related('skill').order_by('-updated_at')
    labels = [us.skill.name for us in user_skills]
    values = [us.progress for us in user_skills]
    return JsonResponse({'labels': labels, 'values': values})


# Skills list/add/edit/delete + icons + practice page
@login_required(login_url='login')
def skills(request):
    user_skills = UserSkill.objects.filter(user=request.user).select_related('skill')
    available_skills = Skill.objects.all()

    # ICON MAP
    devicon_map = {
        "Python": "devicon-python-plain colored",
        "HTML": "devicon-html5-plain colored",
        "CSS": "devicon-css3-plain colored",
        "JavaScript": "devicon-javascript-plain colored",
        "React": "devicon-react-original colored",
        "Django": "devicon-django-plain colored",
        "Java": "devicon-java-plain colored",
        "SQL": "devicon-mysql-plain colored",
        "Git": "devicon-git-plain colored",
        "Node.js": "devicon-nodejs-plain colored",
        "Bootstrap": "devicon-bootstrap-plain colored",
        "Cloud Computing": "devicon-amazonwebservices-plain colored",
    }

    # Add icon_class attribute to each skill
    for s in available_skills:
        s.icon_class = devicon_map.get(s.name, "devicon-code-plain")

    return render(request, "skills.html", {
        "user_skills": user_skills,
        "available_skills": available_skills,
    })



@login_required(login_url='login')
def skill_practice(request, slug):
    skill = get_object_or_404(Skill, slug=slug)

    # Get or create user_skill profile for XP & progress
    user_skill, created = UserSkill.objects.get_or_create(
        user=request.user,
        skill=skill,
        defaults={'progress': 0}
    )

    # Icon logic
    devicon_map = {
        "Python": "devicon-python-plain colored",
        "HTML": "devicon-html5-plain colored",
        "CSS": "devicon-css3-plain colored",
        "JavaScript": "devicon-javascript-plain colored",
        "React": "devicon-react-original colored",
        "Django": "devicon-django-plain colored",
        "Java": "devicon-java-plain colored",
        "SQL": "devicon-mysql-plain colored",
        "Git": "devicon-git-plain colored",
        "Node.js": "devicon-nodejs-plain colored",
        "Bootstrap": "devicon-bootstrap-plain colored",
        "Cloud Computing": "devicon-amazonwebservices-plain colored",
    }
    skill.icon_class = devicon_map.get(skill.name, "devicon-code-plain")

    # All practice tasks for user
    tasks = PracticeQuestion.objects.filter(skill=skill)

    # Auto create UserTask rows so user can track progress
    for t in tasks:
        UserTask.objects.get_or_create(user=request.user, task=t)

    # Overall skill progress %
    total = tasks.count()
    completed = UserTask.objects.filter(
        user=request.user,
        task__skill=skill,
        completed=True
    ).count()
    progress = int((completed / total) * 100) if total > 0 else 0
    user_skill.progress = progress
    user_skill.save()

    # 🔥 NEW — Gamified Difficulty Levels
    difficulties = ["Beginner", "Intermediate", "Advanced", "Expert"]
    colors = {
        "Beginner": "green",
        "Intermediate": "blue",
        "Advanced": "purple",
        "Expert": "red",
    }

    levels = []
    previous_unlocked = True  # Beginner unlocked by default

    for lvl in difficulties:
        total_lvl = PracticeQuestion.objects.filter(skill=skill, difficulty=lvl).count()
        completed_lvl = UserTask.objects.filter(
            user=request.user,
            task__skill=skill,
            task__difficulty=lvl,
            completed=True
        ).count()

        progress_lvl = int((completed_lvl / total_lvl) * 100) if total_lvl > 0 else 0

        unlocked = previous_unlocked
        if progress_lvl < 70:
            previous_unlocked = False

        levels.append({
            'name': lvl,
            'total': total_lvl,
            'completed': completed_lvl,
            'progress': progress_lvl,
            'unlocked': unlocked,
            'color': colors[lvl],
        })
        # 👉 THIS MUST BE INDENTED EXACTLY UNDER THE FUNCTION, NOT FAR LEFT
    return render(request, 'skill_practice.html', {
        'skill': skill,
        'user_skill': user_skill,
        'levels': levels,
        'tasks': tasks,
    })


@login_required
def skill_detail(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    materials = SkillMaterial.objects.filter(skill=skill)
    return render(request, 'skill_detail.html', {
        'skill': skill,
        'materials': materials
    })

@login_required(login_url='login')
def task_detail(request, skill_slug, task_id):
    # get the skill using slug from URL
    skill = get_object_or_404(Skill, slug=skill_slug)
    # get the practice question (task) for that skill
    task = get_object_or_404(PracticeQuestion, id=task_id, skill=skill)

    return render(request, 'task_detail.html', {
        'skill': skill,
        'task': task,
    })

@login_required(login_url='login')
def skill_hub(request, skill_slug, difficulty):
    skill = get_object_or_404(Skill, slug=skill_slug)
    # filter questions based on difficulty OR load materials OR whatever logic you planned


    pdf_count = SkillMaterial.objects.filter(skill=skill, material_type='class_pdf').count()
    notes_count = SkillMaterial.objects.filter(skill=skill).exclude(material_type='class_pdf').count()
    practice_count = PracticeQuestion.objects.filter(skill=skill).count()

    return render(request, 'skill_hub.html', {
        'skill': skill,
        'pdf_count': pdf_count,
        'notes_count': notes_count,
        'practice_count': practice_count,
    })
    

@login_required(login_url='login')
def skill_quiz(request, skill_slug):
    skill = get_object_or_404(Skill, slug=skill_slug)
    user_skill, _ = UserSkill.objects.get_or_create(user=request.user, skill=skill)

    difficulty = request.GET.get('difficulty') or request.POST.get('difficulty')
    context = {'skill': skill, 'difficulty': difficulty}

    # 1) FIRST LOAD → show difficulty selection
    if request.method == "GET" and not difficulty:
        return render(request, 'skill_quiz.html', context)

    # 2) GET with difficulty → show quiz questions
    if request.method == "GET" and difficulty:
        questions_qs = PracticeQuestion.objects.filter(
            skill=skill,
            difficulty=difficulty,
            question_type='MCQ',  # quiz will be MCQ
        )

        total_available = questions_qs.count()
        if total_available == 0:
            context['no_questions'] = True
            return render(request, 'skill_quiz.html', context)

        # limit to 5 questions
        questions = questions_qs.order_by('?')[:5]

        context.update({
            'questions': questions,
            'total_questions': questions.count(),
        })
        return render(request, 'skill_quiz.html', context)

    # 3) POST → calculate score, give XP, mark completed
    if request.method == "POST" and difficulty:
        # question_ids comes as comma separated list
        ids_raw = request.POST.get('question_ids', '')
        if not ids_raw:
            context['no_questions'] = True
            return render(request, 'skill_quiz.html', context)

        q_ids = [int(qid) for qid in ids_raw.split(',') if qid.strip().isdigit()]
        questions = PracticeQuestion.objects.filter(id__in=q_ids, skill=skill)

        results = []
        score = 0
        total = questions.count()
        total_xp_earned = 0

        for q in questions:
            key = f"answer_{q.id}"
            user_answer = request.POST.get(key, '').strip()
            is_correct = (user_answer == q.correct_option)

            # track completion per question
            user_task, _ = UserTask.objects.get_or_create(user=request.user, task=q)

            if is_correct:
                score += 1
                # XP only once per question
                if not user_task.completed:
                    user_task.completed = True
                    user_task.save()
                    user_skill.add_xp(q.xp_reward)
                    total_xp_earned += q.xp_reward

            results.append({
                'question': q,
                'user_answer': user_answer or "Not answered",
                'correct_answer': q.correct_option,
                'is_correct': is_correct,
            })

        # Update skill progress (same logic as before)
        total_questions = PracticeQuestion.objects.filter(skill=skill).count()
        completed_questions = UserTask.objects.filter(
            user=request.user,
            task__skill=skill,
            completed=True
        ).count()
        user_skill.progress = int((completed_questions / total_questions) * 100) if total_questions > 0 else 0
        user_skill.save()

        percentage = math.floor((score / total) * 100) if total > 0 else 0

        context.update({
            'results': results,
            'score': score,
            'total_questions': total,
            'percentage': percentage,
            'total_xp_earned': total_xp_earned,
        })
        return render(request, 'skill_quiz.html', context)



@login_required
def task_open(request, slug, task_id):
    skill = get_object_or_404(Skill, slug=slug)
    user_skill, created = UserSkill.objects.get_or_create(
        user=request.user,
        skill=skill
    )

    # Increase progress automatically
    user_skill.progress = min(100, user_skill.progress + 8)
    user_skill.save()

    return redirect('skill_practice', slug=slug)

@require_POST
@login_required(login_url='login')
def complete_task(request):
    """
    Accepts JSON: { "skill_slug": "...", "task_id": 1 }
    Marks a task as completed (simple approach) and updates UserSkill.progress.
    Returns JSON: { "progress": new_progress, "task_completed": True }
    """

    try:
        payload = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    skill_slug = payload.get('skill_slug')
    task_id = payload.get('task_id')

    if not skill_slug or not task_id:
        return HttpResponseBadRequest("Missing fields")

    skill = get_object_or_404(Skill, slug=skill_slug)

    # Ensure user_skill exists (create if missing)
    user_skill, _ = UserSkill.objects.get_or_create(user=request.user, skill=skill)

    # For now we treat the problem set as fixed length.
    # You can store real Task models later. Here we assume 3 tasks.
    total_tasks = 3

    # track completed tasks -- simplest approach: store completed ids in cache or a small JSONField on UserSkill
    # If you don't have a field, we will create a simple `completed_tasks` JSON store on Profile or UserSkill.
    # Below is a safe approach: use a small JSONField on UserSkill called `meta` (if not present, fallback)
    # For this example, we'll try to attach a Python attribute on user_skill (not persistent) if model not changed.
    # Better: add a JSONField to UserSkill (recommended). For quickness, we'll persist completed_task ids as comma string in a new field
    #
    # --- quick implementation using a JSONField named `completed_tasks` on UserSkill if present ---

    completed = []
    if hasattr(user_skill, 'completed_tasks'):
        # assumed JSONField (list)
        completed = user_skill.completed_tasks or []
    else:
        # fallback: try to use attribute `_completed_tasks_cache` (non persistent)
        completed = getattr(user_skill, '_completed_tasks_cache', [])

    if task_id in completed:
        # already done
        return JsonResponse({'progress': user_skill.progress, 'task_completed': False})

    # mark completed
    completed.append(task_id)

    # persist if model has field
    if hasattr(user_skill, 'completed_tasks'):
        user_skill.completed_tasks = completed

    # or cache to attribute (non persistent)
    setattr(user_skill, '_completed_tasks_cache', completed)

    # compute progress step
    increment = ceil(100 / total_tasks)
    new_progress = min(100, (user_skill.progress or 0) + increment)
    user_skill.progress = new_progress
    user_skill.save()

    # optionally: return extra info (num completed etc)
    return JsonResponse({'progress': new_progress, 'task_completed': True})




@login_required(login_url='login')
@require_POST
def add_skill(request):
    name = request.POST.get('skill_name')
    progress = request.POST.get('progress') or 0
    try:
        progress = int(progress)
    except ValueError:
        progress = 0

    skill_obj, _ = Skill.objects.get_or_create(name=name)
    if not skill_obj.slug:
        skill_obj.slug = skill_obj.name.lower().replace(' ', '-')
        skill_obj.save()

    user_skill, _ = UserSkill.objects.get_or_create(user=request.user, skill=skill_obj)
    user_skill.progress = progress
    user_skill.save()

    messages.success(request, f"Added/updated skill: {skill_obj.name} ({user_skill.progress}%)")
    return redirect('skills')


@login_required(login_url='login')
def edit_skill(request, skill_id):
    us = get_object_or_404(UserSkill, id=skill_id, user=request.user)
    if request.method == 'POST':
        try:
            p = int(request.POST.get('progress', us.progress))
            us.progress = max(0, min(100, p))
            us.save()
            messages.success(request, "Progress updated.")
            return redirect('dashboard')
        except ValueError:
            messages.error(request, "Invalid progress value.")
    return render(request, 'edit_skill.html', {'user_skill': us})


@login_required(login_url='login')
def delete_skill(request, skill_id):
    user_skill = get_object_or_404(UserSkill, id=skill_id, user=request.user)
    if request.method == 'POST':
        skill_name = user_skill.skill.name
        user_skill.delete()
        messages.success(request, f"🗑️ '{skill_name}' has been deleted successfully.")
        return redirect('skills')
    messages.error(request, "Something went wrong while deleting.")
    return redirect('skills')

@login_required
def skill_progress(request):
    user_skills = UserSkill.objects.filter(user=request.user)
    return render(request, "app/skill_progress.html", {"user_skills": user_skills})

# Internships / Apply / Profile are kept the same
@login_required(login_url='login')
def internships(request):
    internships = MicroInternship.objects.all().order_by('-id')
    return render(request, 'internships.html', {'internships': internships})


@login_required(login_url='login')
def apply_internship(request):
    if request.method == 'POST':
        internship_id = request.POST.get('internship_id')
        motivation = request.POST.get('motivation', '')
        internship = get_object_or_404(MicroInternship, id=internship_id)
        if Application.objects.filter(user=request.user, internship=internship).exists():
            messages.warning(request, "⚠️ You’ve already applied for this internship.")
            return redirect('internships')
        Application.objects.create(user=request.user, internship=internship, motivation=motivation, status='Pending')
        messages.success(request, "✅ Application submitted successfully!")
        return redirect('internships')
    return redirect('internships')


@login_required
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    user_skills = UserSkill.objects.filter(user=request.user)
    applications = Application.objects.filter(user=request.user)
    total_skills = user_skills.count()
    total_internships = applications.count()
    avg_progress = 0
    if total_skills > 0:
        avg_progress = int(sum(s.progress for s in user_skills) / total_skills)
    return render(request, 'profile.html', {
        'profile': profile,
        'total_skills': total_skills,
        'total_internships': total_internships,
        'avg_progress': avg_progress,
    })


@login_required
def edit_profile(request):
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
