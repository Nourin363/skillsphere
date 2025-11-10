from django.db import models
from django.contrib.auth.models import User

# --------------------------- PROFILE ---------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', default='default.png', blank=True)
    skills_summary = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


# --------------------------- SKILL ---------------------------
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# --------------------------- USER SKILL ---------------------------
class UserSkill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    progress = models.PositiveIntegerField(default=0)  # safer than plain IntegerField (no negatives)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'skill')  # ensures a user doesn’t duplicate same skill

    def __str__(self):
        return f"{self.user.username} - {self.skill.name} ({self.progress}%)"


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
