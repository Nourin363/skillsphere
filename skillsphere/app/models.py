from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

# --------------------------- PROFILE ---------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', default='default.png', blank=True)
    skills_summary = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# --------------------------- SKILL ---------------------------
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# --------------------------- USER SKILL ---------------------------
class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('web', 'Web Development'),
        ('programming', 'Programming'),
        ('data', 'Data & Analytics'),
        ('mobile', 'Mobile Development'),
        ('soft', 'Soft Skills'),
        ('other', 'Other'),
    ]

    DIFFICULTY_CHOICES = [
    ('Beginner', 'Beginner'),
    ('Intermediate', 'Intermediate'),
    ('Advanced', 'Advanced'),
    ('Expert', 'Expert'),
]


    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    
    icon = models.CharField(max_length=100, blank=True, null=True)   # DEVICON CLASS

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



# --------------------------- USER SKILL ---------------------------
class UserSkill(models.Model):
    DIFFICULTY_LEVELS = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey('Skill', on_delete=models.CASCADE)
    level = models.PositiveIntegerField(default=1)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='Beginner')
    xp = models.PositiveIntegerField(default=0)      # XP gained from tasks & internships
    progress = models.PositiveIntegerField(default=0)  # 0–100 visual progress bar

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'skill')

    def __str__(self):
        return f"{self.user.username} - {self.skill.name}"

# 🔥 Level-up logic — called whenever XP increases
    def add_xp(self, amount):
        self.xp += amount
        required_xp = 100 + (self.level - 1) * 50

        level_up = False

        while self.xp >= required_xp:
            self.xp -= required_xp
            self.level += 1
            level_up = True
            required_xp = 100 + (self.level - 1) * 50

        self.progress = int((self.xp / required_xp) * 100)
        self.save()

        return level_up






# Each skill has multiple practice tasks
class PracticeQuestion(models.Model):
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('SHORT', 'Short Answer'),
        ('CODE', 'Coding'),
    ]

    DIFFICULTY_LEVELS = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert'),
    ]

    skill = models.ForeignKey('Skill', on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='MCQ')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='Beginner')

    question_text = models.TextField()

    # MCQ options (used only when question_type == 'MCQ')
    option_a = models.CharField(max_length=255, blank=True)
    option_b = models.CharField(max_length=255, blank=True)
    option_c = models.CharField(max_length=255, blank=True)
    option_d = models.CharField(max_length=255, blank=True)

    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        blank=True
    )

    # For SHORT or CODE type questions
    correct_text_answer = models.TextField(blank=True)

    # XP auto-determined from difficulty
    xp_reward = models.PositiveIntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.skill.name} ({self.difficulty}) - {self.question_text[:40]}"

    def save(self, *args, **kwargs):
        # Auto set XP based on difficulty (Option A)
        xp_map = {
            'Beginner': 5,
            'Intermediate': 10,
            'Advanced': 15,
            'Expert': 20,
        }
        self.xp_reward = xp_map.get(self.difficulty, 5)
        super().save(*args, **kwargs)


# Tracks which user completed which task
class UserTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(PracticeQuestion, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'task')

    def __str__(self):
        return f"{self.user.username} - {self.task.title} ({'Done' if self.completed else 'Pending'})"



# --------------------------- MICRO INTERNSHIP ---------------------------
class MicroInternship(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    skill_required = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='internships')
    duration_weeks = models.IntegerField(default=1)
    reward_points = models.PositiveIntegerField(default=50)
    mentor = models.CharField(max_length=100, default="AI Mentor")
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class InternshipTask(models.Model):
    internship = models.ForeignKey(
        MicroInternship,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=1)  # Task 1, 2, 3...
    reward_points = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.internship.title} - Task {self.order}: {self.title}"



# --------------------------- APPLICATION ---------------------------
class Application(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    internship = models.ForeignKey(MicroInternship, on_delete=models.CASCADE)
    motivation = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'internship')  # prevent duplicate applications

    def __str__(self):
        return f"{self.user.username} → {self.internship.title} ({self.status})"

# --------------------------- ACHIEVEMENT ---------------------------
class Achievement(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.ImageField(upload_to='achievements/', blank=True, null=True)

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_on = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_on = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"To {self.user.username}: {self.message[:25]}"


class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=50)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    session_duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} logged in"


class SkillMaterial(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='skill_materials/', blank=True)
    material_type = models.CharField(max_length=50, choices=[
        ('question', 'Question'),
        ('task', 'Task'),
        ('quiz', 'Quiz'),
        ('class_pdf', 'Class PDF'),
    ])

    created_at = models.DateTimeField(auto_now_add=True)

# class Task(models.Model):
#     DIFFICULTY_CHOICES = [
#         ('Easy', 'Easy'),
#         ('Medium', 'Medium'),
#         ('Hard', 'Hard'),
#     ]

#     skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
#     file = models.FileField(upload_to='task_files/', blank=True, null=True)  # optional PDF/image
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title
