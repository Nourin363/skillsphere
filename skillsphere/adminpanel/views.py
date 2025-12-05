from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from app.models import UserSkill, Skill, SkillMaterial, Profile, Notification
from django.db.models import Q, Sum, Avg
from app.models import LoginLog
from django.utils import timezone
from django.contrib.auth import logout
# from adminpanel.views import get_client_ip


# from django.contrib.auth.models import User
# from django.contrib import messages
# from django.shortcuts import render, redirect
# from app.models import Profile  # if needed

# Import models from main app
from app.models import (
    Profile,
    Skill,
    MicroInternship,
    Application,
    PracticeQuestion,
    InternshipTask,   # <-- only if you already created this model
)

def is_admin(user):
    return user.is_superuser

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')



def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get("next") or request.GET.get("next")

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return redirect("login")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # ⭐ Log login event
            LoginLog.objects.create(
                user=user,
                ip_address=get_client_ip(request),
                login_time=timezone.now()
            )

            if next_url:
                return redirect(next_url)

            return redirect("admin_dashboard" if user.is_superuser else "dashboard")

        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "login.html")



def login_logs(request):
    logs = LoginLog.objects.select_related('user').order_by('-login_time')
    return render(request, "adminpanel/logs.html", {"logs": logs})

def admin_logout(request):
    latest_log = LoginLog.objects.filter(
        user=request.user,
        logout_time__isnull=True
    ).order_by('-login_time').first()

    if latest_log:
        latest_log.logout_time = timezone.now()
        latest_log.session_duration = latest_log.logout_time - latest_log.login_time
        latest_log.save()

    logout(request)
    return redirect('index')

@login_required
@user_passes_test(is_admin)
def admin_skills(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category = request.POST.get('category')
        difficulty = request.POST.get('difficulty')
        icon = request.POST.get('icon')
        icon_custom = request.POST.get('icon_custom')

        if icon_custom:  
            icon = icon_custom


        if not name:
            messages.error(request, "Skill name is required.")
        else:
            Skill.objects.create(
                name=name,
                description=description,
                category=category,
                difficulty=difficulty,
                icon=icon
            )
            messages.success(request, f"Skill '{name}' added successfully!")
            return redirect('admin_skills')

    skills = Skill.objects.all().order_by('name')
    return render(request, 'adminpanel/manage_skills.html', {
        'skills': skills,
        'categories': Skill.CATEGORY_CHOICES,
        'difficulties': Skill.DIFFICULTY_CHOICES,
    })


@login_required
@user_passes_test(is_admin)
def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    skill.delete()
    messages.success(request, "Skill deleted.")
    return redirect('admin_skills')


@user_passes_test(is_admin, login_url='login')
def admin_dashboard(request):
    context = {
    "total_skills": Skill.objects.count(),
    "total_internships": MicroInternship.objects.count(),
    "total_applications": Application.objects.count(),
    "total_users": User.objects.count(),
    }

    return render(request, 'adminpanel/dashboard.html', context)
        

# Allow only admin users to access (your custom admin panel)
def is_admin(user):
    return user.is_staff  # or check role if you use custom roles

@login_required
@user_passes_test(is_admin)
def admin_skill_detail(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    materials = SkillMaterial.objects.filter(skill=skill)

    return render(request, 'admin/skill_detail.html', {
        'skill': skill,
        'materials': materials
    })



@login_required
def admin_user_skills(request):
    """
    Admin overview: one card per user, with filters + sorting.
    """
    user_skills = UserSkill.objects.select_related("user", "skill")
    skills = Skill.objects.all()

    # 🔍 Search
    search = request.GET.get("search")
    if search:
        user_skills = user_skills.filter(
            Q(user__username__icontains=search)
            | Q(skill__name__icontains=search)
        )

    # 🎯 Filter by skill
    skill_filter = request.GET.get("skill")
    if skill_filter:
        user_skills = user_skills.filter(skill__name=skill_filter)

    # 🎯 Filter by difficulty
    difficulty_filter = request.GET.get("difficulty")
    if difficulty_filter:
        user_skills = user_skills.filter(difficulty=difficulty_filter)

    # 🔽 Sorting
    sort = request.GET.get("sort")
    if sort:
        if sort == "username":
            user_skills = user_skills.order_by("user__username")
        elif sort in ["-xp", "-level", "-progress"]:
            user_skills = user_skills.order_by(sort)

    # 👥 unique users after all filters/sorting
    users = list({us.user for us in user_skills})

    return render(
        request,
        "adminpanel/admin_user_skills.html",
        {
            "users": users,
            "skills": skills,
            "request": request,  # for keeping filter values
        },
    )


def admin_user_skill_detail(request, user_id):
    """
    Per-user skill dashboard: summary + skill cards.
    """
    user = get_object_or_404(User, id=user_id)

    skills_qs = (
        UserSkill.objects.filter(user=user)
        .select_related("skill")
        .order_by("-progress")
    )

    total_xp = skills_qs.aggregate(total=Sum("xp"))["total"] or 0
    avg_progress = skills_qs.aggregate(avg=Avg("progress"))["avg"] or 0
    total_skills = skills_qs.count()
    highest_level_obj = skills_qs.order_by("-level").first()
    highest_level = highest_level_obj.level if highest_level_obj else 0

    context = {
        "user_obj": user,
        "skills_qs": skills_qs,
        "total_xp": total_xp,
        "avg_progress": int(avg_progress) if avg_progress else 0,
        "total_skills": total_skills,
        "highest_level": highest_level,
    }
    return render(
        request,
        "adminpanel/admin_user_skill_detail.html",
        context,
    )


@user_passes_test(is_admin, login_url='login')
def admin_skills(request):
    skills = Skill.objects.all()
    return render(request, 'adminpanel/manage_skills.html', {'skills': skills})

@user_passes_test(is_admin, login_url='login')
def add_skill(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        Skill.objects.create(name=name, description=description)
        messages.success(request, "Skill added successfully!")
        return redirect('admin_skills')
    return render(request, 'adminpanel/add_skill.html')

@user_passes_test(is_admin, login_url='login')
def edit_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    if request.method == "POST":
        skill.name = request.POST.get("name")
        skill.description = request.POST.get("description")
        skill.save()
        messages.success(request, "Skill updated successfully!")
        return redirect('admin_skills')
    return render(request, 'adminpanel/edit_skill.html', {'skill': skill})

@user_passes_test(is_admin, login_url='login')
def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    skill.delete()
    messages.success(request, "Skill deleted successfully!")
    return redirect('admin_skills')


# def admin_questions_placeholder(request):
    # return HttpResponse("Practice questions management coming soon.")

def manage_internships(request):
    skills = Skill.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        skill_id = request.POST.get('skill_required')
        duration = request.POST.get('duration_weeks')
        reward = request.POST.get('reward_points')

        skill = Skill.objects.get(id=skill_id)
        MicroInternship.objects.create(
            title=title,
            description=description,
            skill_required=skill,
            duration_weeks=duration,
            reward_points=reward
        )
        messages.success(request, "Internship added successfully!")
        return redirect('manage_internships')

    internships = MicroInternship.objects.select_related('skill_required').all()
    return render(request, 'adminpanel/manage_internships.html', {
        'skills': skills,
        'internships': internships
    })


# def add_internship(request):
    # if request.method == 'POST':
    #     title = request.POST.get('title')
    #     description = request.POST.get('description')
    #     skill_required = Skill.objects.get(id=request.POST.get('skill_required'))
    #     duration_weeks = request.POST.get('duration_weeks')
    #     reward_points = request.POST.get('reward_points')

    #     MicroInternship.objects.create(
    #         title=title,
    #         description=description,
    #         skill_required=skill_required,
    #         duration_weeks=duration_weeks,
    #         reward_points=reward_points,
    #     )
    #     messages.success(request, "Internship added successfully")
    #     return redirect('manage_internships')

    # skills = Skill.objects.all()
    # return render(request, 'adminpanel/add_internship.html', {'skills': skills})

def delete_internship(request, internship_id):
    obj = get_object_or_404(MicroInternship, id=internship_id)
    obj.delete()
    messages.success(request, "Internship deleted")
    return redirect('manage_internships')

# # def admin_updates_placeholder(request):
#     return HttpResponse("Updates module coming soon.")


def manage_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'adminpanel/manage_users.html', {'users': users})

def block_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.profile.is_blocked = True
    user.profile.save()
    messages.success(request, f"{user.username} has been blocked")
    return redirect('manage_users')

def unblock_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.profile.is_blocked = False
    user.profile.save()
    messages.success(request, f"{user.username} has been unblocked")
    return redirect('manage_users')

def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully")
    return redirect('manage_users')

# ---------- ADMIN: MANAGE TASKS ----------

def manage_tasks(request):
    skill_tasks = PracticeQuestion.objects.select_related('skill').all()
    internship_tasks = InternshipTask.objects.select_related('internship').all()
    return render(request, 'adminpanel/manage_tasks.html', {
        'skill_tasks': skill_tasks,
        'internship_tasks': internship_tasks,
    })


def add_skill_task(request):
    skills = Skill.objects.all()

    if request.method == 'POST':
        skill_id = request.POST.get('skill')
        question_text = request.POST.get('title')  # UI calls it title, model calls it question_text
        difficulty = request.POST.get('difficulty', 'Beginner')

        skill = Skill.objects.get(id=skill_id)

        PracticeQuestion.objects.create(
            skill=skill,
            question_text=question_text,
            difficulty=difficulty,
            question_type='MCQ'   # default preset (we can allow selection later)
        )

        messages.success(request, "Skill practice question added successfully.")
        return redirect('manage_tasks')

    return render(request, 'adminpanel/add_skill_task.html', {'skills': skills})

def edit_skill_task(request, task_id):
    task = get_object_or_404(PracticeQuestion, id=task_id)

    if request.method == "POST":
        task.skill_id = request.POST.get("skill")
        task.question_text = request.POST.get("question_text")
        task.difficulty = request.POST.get("difficulty")
        task.save()
        messages.success(request, "Skill task updated successfully.")
        return redirect("manage_tasks")

    skills = Skill.objects.all()
    return render(request, "adminpanel/edit_skill_task.html", {
        "task": task,
        "skills": skills
    })



def delete_skill_task(request, task_id):
    task = get_object_or_404(PracticeQuestion, id=task_id)
    task.delete()
    messages.success(request, "Skill task deleted.")
    return redirect('manage_tasks')


def add_internship_task(request):
    if request.method == 'POST':
        internship_id = request.POST.get('internship')
        title = request.POST.get('title')
        description = request.POST.get('description')
        order = request.POST.get('order') or 1
        reward_points = request.POST.get('reward_points') or 10

        internship = MicroInternship.objects.get(id=internship_id)
        InternshipTask.objects.create(
            internship=internship,
            title=title,
            description=description,
            order=order,
            reward_points=reward_points,
        )
        messages.success(request, "Internship task added.")
        return redirect('manage_tasks')

    internships = MicroInternship.objects.all()
    return render(request, 'adminpanel/add_internship_task.html', {
        'internships': internships
    })


def delete_internship_task(request, task_id):
    task = get_object_or_404(InternshipTask, id=task_id)
    task.delete()
    messages.success(request, "Internship task deleted.")
    return redirect('manage_tasks')

# ---------- ADMIN: ANNOUNCEMENTS ----------


def admin_announcements(request):
    return render(request, 'adminpanel/announcements.html')

def admin_logs(request):
    return render(request, 'adminpanel/logs.html')

def admin_leaderboard(request):
    selected_skill = request.GET.get("skill")

    skills = Skill.objects.all()

    if selected_skill:
        user_skills = UserSkill.objects.filter(skill__name=selected_skill).order_by("-xp")
    else:
        user_skills = []  # No skill selected yet

    top_three = user_skills[:3]
    remaining = user_skills[3:]

    chart_labels = [us.user.username for us in user_skills[:10]]
    chart_data = [us.xp for us in user_skills[:10]]

    return render(request, "adminpanel/admin_leaderboard.html", {
        "skills": skills,
        "selected_skill": selected_skill,
        "top_three": top_three,
        "remaining": remaining,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
    })

def admin_users(request):
    search = request.GET.get("search", "")
    users = User.objects.filter(username__icontains=search).order_by("username")
    return render(request, "adminpanel/admin_users.html", {"users": users, "search": search})


def block_user(request, user_id):
    profile = Profile.objects.get(user_id=user_id)
    profile.is_blocked = True
    profile.save()
    return redirect("admin_users")


def unblock_user(request, user_id):
    profile = Profile.objects.get(user_id=user_id)
    profile.is_blocked = False
    profile.save()
    return redirect("admin_users")


def send_announcement(request, user_id):
    if request.method == "POST":
        message = request.POST.get("message")
        Notification.objects.create(user_id=user_id, message=message)
        return redirect("admin_users")

    user = User.objects.get(id=user_id)
    return render(request, "adminpanel/send_announcement.html", {"user": user})

def send_update(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        title = request.POST.get('title')
        message = request.POST.get('message')

        # Create notification for the selected user
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type="update"  # helps user dashboard categorize it
        )

        messages.success(request, f"Update sent to {user.username} successfully!")
        return redirect('manage_users')   # redirect back to users table

    return render(request, 'adminpanel/send_update.html', {'user': user})



def admin_questions(request):
    skill_filter = request.GET.get("skill", "")
    difficulty_filter = request.GET.get("difficulty", "")

    questions = PracticeQuestion.objects.select_related('skill').order_by('-created_at')
    skills = Skill.objects.all()

    if skill_filter:
        questions = questions.filter(skill__id=skill_filter)

    if difficulty_filter:
        questions = questions.filter(difficulty=difficulty_filter)

    context = {
        "questions": questions,
        "skills": skills,
        "skill_filter": skill_filter,
        "difficulty_filter": difficulty_filter,
    }
    return render(request, "adminpanel/admin_questions.html", context)


def admin_add_question(request):
    skills = Skill.objects.all()

    if request.method == "POST":
        skill_id = request.POST.get("skill")
        question_type = request.POST.get("question_type")
        difficulty = request.POST.get("difficulty")
        question_text = request.POST.get("question_text")

        option_a = request.POST.get("option_a", "")
        option_b = request.POST.get("option_b", "")
        option_c = request.POST.get("option_c", "")
        option_d = request.POST.get("option_d", "")
        correct_option = request.POST.get("correct_option", "")
        correct_text_answer = request.POST.get("correct_text_answer", "")

        skill = Skill.objects.get(id=skill_id)

        PracticeQuestion.objects.create(
            skill=skill,
            question_type=question_type,
            difficulty=difficulty,
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option,
            correct_text_answer=correct_text_answer,
        )

        messages.success(request, "Practice question added successfully.")
        return redirect("admin_questions")

    return render(request, "adminpanel/admin_add_question.html", {"skills": skills})


def admin_edit_question(request, pk):
    question = PracticeQuestion.objects.get(pk=pk)
    skills = Skill.objects.all()

    if request.method == "POST":
        skill_id = request.POST.get("skill")
        question_type = request.POST.get("question_type")
        difficulty = request.POST.get("difficulty")
        question_text = request.POST.get("question_text")

        option_a = request.POST.get("option_a", "")
        option_b = request.POST.get("option_b", "")
        option_c = request.POST.get("option_c", "")
        option_d = request.POST.get("option_d", "")
        correct_option = request.POST.get("correct_option", "")
        correct_text_answer = request.POST.get("correct_text_answer", "")

        question.skill = Skill.objects.get(id=skill_id)
        question.question_type = question_type
        question.difficulty = difficulty
        question.question_text = question_text
        question.option_a = option_a
        question.option_b = option_b
        question.option_c = option_c
        question.option_d = option_d
        question.correct_option = correct_option
        question.correct_text_answer = correct_text_answer

        question.save()
        messages.success(request, "Practice question updated successfully.")
        return redirect("admin_questions")

    return render(
        request,
        "adminpanel/admin_edit_question.html",
        {"question": question, "skills": skills},
    )


def admin_delete_question(request, pk):
    question = PracticeQuestion.objects.get(pk=pk)
    question.delete()
    messages.success(request, "Practice question deleted.")
    return redirect("admin_questions")

@login_required
def add_skill_material(request):
    if not request.user.is_staff:
        return redirect("dashboard")

    if request.method == "POST":
        skill_id = request.POST.get("skill")
        title = request.POST.get("title")
        description = request.POST.get("description")
        material_type = request.POST.get("material_type")
        file = request.FILES.get("file")

        skill = Skill.objects.get(id=skill_id)

        SkillMaterial.objects.create(
            skill=skill,
            title=title,
            description=description,
            material_type=material_type,
            file=file
        )
        
        # 📌 For notifications — trigger after upload (PHASE B)
        Notification.objects.create(
            user=None,  # will later apply "for all learners"
            message=f"New {material_type} added for {skill.name}!"
        )

        messages.success(request, "Material uploaded successfully!")
        return redirect("add_skill_material")

    skills = Skill.objects.all()
    return render(request, "adminpanel/add_skill_material.html", {"skills": skills})

@login_required
def admin_materials(request):
    skill_filter = request.GET.get("skill", "")
    materials = SkillMaterial.objects.select_related('skill').order_by('-created_at')
    skills = Skill.objects.all()

    if skill_filter:
        materials = materials.filter(skill__id=skill_filter)

    context = {
        "materials": materials,
        "skills": skills,
        "skill_filter": skill_filter,
    }
    return render(request, "adminpanel/admin_materials.html", context)

@login_required
def admin_add_material(request):
    skills = Skill.objects.all()

    if request.method == "POST":
        skill_id = request.POST.get("skill")
        title = request.POST.get("title")
        description = request.POST.get("description")
        material_type = request.POST.get("material_type")
        file = request.FILES.get("file")

        skill = Skill.objects.get(id=skill_id)

        SkillMaterial.objects.create(
            skill=skill,
            title=title,
            description=description,
            material_type=material_type,
            file=file
        )

        messages.success(request, "Study material uploaded successfully.")
        return redirect("admin_materials")

    return render(request, "adminpanel/admin_add_material.html", {"skills": skills})

@login_required
def admin_delete_material(request, pk):
    material = get_object_or_404(SkillMaterial, pk=pk)
    material.delete()
    messages.success(request, "Study material deleted.")
    return redirect("admin_materials")
