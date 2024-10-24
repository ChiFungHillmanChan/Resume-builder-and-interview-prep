from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import (
    CustomLoginView, 
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView
)

urlpatterns = [
    path('', views.home, name='home'),
   
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', 
        CustomPasswordResetConfirmView.as_view(), 
        name='password_reset_confirm'),
    path('password-reset/complete/', 
        CustomPasswordResetCompleteView.as_view(), 
        name='password_reset_complete'),
    path('register/', views.register, name='register'),

    path('ai_job_info/', views.ai_job_info, name='ai_job_info'),
    path('user-profile/', views.user_profile, name='user_profile'),

    path('cv-analysis/', views.cv_analysis, name='cv_analysis'),

    path('resume-builder/', views.resume_builder, name='resume_builder'),
    path('delete-experience/<int:experience_id>/', views.delete_experience, name='delete_experience'),
    path('delete-education/<int:education_id>/', views.delete_education, name='delete_education'),
    path('delete-skill/<int:skill_id>/', views.delete_skill, name='delete_skill'),
]