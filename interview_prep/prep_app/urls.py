from django.urls import path, include
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
    path('social-auth/', include('social_django.urls', namespace='social')),

    path('ai_job_info/', views.ai_job_info, name='ai_job_info'),
    path('user-profile/', views.user_profile, name='user_profile'),

    path('cv-analysis/', views.cv_analysis, name='cv_analysis'),

    path('resume-builder/', views.resume_builder, name='resume_builder'),
    path('customer-support/', views.customer_support, name='customer_support'),
    path('delete-experience/<int:experience_id>/', views.delete_experience, name='delete_experience'),
    path('delete-education/<int:education_id>/', views.delete_education, name='delete_education'),
    path('delete-skill/<int:skill_id>/', views.delete_skill, name='delete_skill'),

    path('interview-prep/', views.topic_list, name='interview_prep'),
    path('topic/<slug:topic_slug>/', views.question_list, name='question_list'),
    path('question/<int:question_id>/', views.coding_assessment, name='coding_assessment'),
    path('question/<int:question_id>/run/', views.run_code, name='run_code'),
    path('question/<int:question_id>/save_code', views.save_code, name='save_code'),
    path('question/<int:question_id>/get_saved_code', views.get_saved_code, name='get_saved_code'),
]