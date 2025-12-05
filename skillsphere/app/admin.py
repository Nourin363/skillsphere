from django.contrib import admin
from .models import Skill, UserSkill, MicroInternship, Application, Profile, Achievement, UserAchievement, UserTask, PracticeQuestion
from .models import SkillMaterial

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')           # category removed
    search_fields = ('name',)                 # category removed

@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'difficulty', 'progress', 'updated_at')

@admin.register(MicroInternship)
class MicroInternshipAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_on')
    search_fields = ('title',)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'internship', 'status', 'applied_on')
    list_filter = ('status',)
    search_fields = ('user__username', 'internship__title')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username',)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_on')
    search_fields = ('user__username', 'achievement__name')

class SkillMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'skill', 'material_type', 'created_at')
    list_filter = ('skill', 'material_type')
    search_fields = ('title', 'skill__name')
admin.site.register(SkillMaterial, SkillMaterialAdmin)

class PracticeQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'skill', 'question_type', 'difficulty', 'xp_reward', 'created_at')
    list_filter = ('skill', 'question_type', 'difficulty')
    search_fields = ('question_text', 'skill__name')

admin.site.register(PracticeQuestion, PracticeQuestionAdmin)