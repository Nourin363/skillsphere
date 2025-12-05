from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path("logs/", views.login_logs, name="login_logs"),
    path('logout/', views.admin_logout, name='admin_logout'),


    # Skill Management
    path('skills/', views.admin_skills, name='admin_skills'),
    path('skills/add/', views.add_skill, name='admin_add_skill'),
    path('skills/edit/<int:skill_id>/', views.edit_skill, name='admin_edit_skill'),
    path('skills/delete/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path('admin/user-skills/', views.admin_user_skills, name='admin_user_skills'),
    path("admin/user-skills/<int:user_id>/", views.admin_user_skill_detail, name="admin_user_skill_detail"),
    path('admin-panel/skill/<int:skill_id>/', views.admin_skill_detail, name='admin_skill_detail'),
    path("materials/", views.admin_materials, name="admin_materials"),
    path("materials/add/", views.admin_add_material, name="admin_add_material"),
    path("materials/delete/<int:pk>/", views.admin_delete_material, name="admin_delete_material"),




    # Temporary placeholders to prevent errors
    # path('questions/', views.admin_questions_placeholder, name='admin_questions'),
    # path('internships/', views.admin_internships_placeholder, name='admin_internships'),
    # path('updates/', views.admin_updates_placeholder, name='admin_updates'),

    path('users/', views.manage_users, name='manage_users'),
    path('users/block/<int:user_id>/', views.block_user, name='block_user'),
    path('users/unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    path('internships/', views.manage_internships, name='manage_internships'),
    # path('internships/add/', views.add_internship, name='add_internship'),
    path('internships/delete/<int:internship_id>/', views.delete_internship, name='delete_internship'),

        # TASKS
    path('tasks/', views.manage_tasks, name='manage_tasks'),
    path('tasks/add-skill/', views.add_skill_task, name='add_skill_task'),
    path('tasks/edit/<int:task_id>/', views.edit_skill_task, name='edit_skill_task'),
    path('tasks/delete-skill/<int:task_id>/', views.delete_skill_task, name='delete_skill_task'),
    path('tasks/add-internship/', views.add_internship_task, name='add_internship_task'),
    path('tasks/delete-internship/<int:task_id>/', views.delete_internship_task, name='delete_internship_task'),
    path("admin/leaderboard/", views.admin_leaderboard, name="admin_leaderboard"),


    path('announcements/', views.admin_announcements, name='admin_announcements'),
    path('logs/', views.admin_logs, name='admin_logs'),

    path("admin/users/", views.admin_users, name="admin_users"),
    path("admin/users/block/<int:user_id>/", views.block_user, name="block_user"),
    path("admin/users/unblock/<int:user_id>/", views.unblock_user, name="unblock_user"),
    path("admin/users/announce/<int:user_id>/", views.send_announcement, name="send_announcement"),

    path("admin/questions/", views.admin_questions, name="admin_questions"),
    path("admin/questions/add/", views.admin_add_question, name="admin_add_question"),
    path("admin/questions/<int:pk>/edit/", views.admin_edit_question, name="admin_edit_question"),
    path("admin/questions/<int:pk>/delete/", views.admin_delete_question, name="admin_delete_question"),

    path('send-update/<int:user_id>/', views.send_update, name='send_update'),


]

