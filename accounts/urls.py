from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import StrictPasswordResetForm

urlpatterns = [
    path('about/', views.about_view, name='about'),
    path('contact-us/', views.contact_us_view, name='contact_us'),
    # --- Topic API endpoints for admin upload dashboard ---
    path('api/topics/', views.api_list_topics, name='api_list_topics'),
    path('api/topics/create/', views.api_create_topic, name='api_create_topic'),
    path('api/topics/<int:topic_id>/update/', views.api_update_topic, name='api_update_topic'),
    path('api/topics/<int:topic_id>/delete/', views.api_delete_topic, name='api_delete_topic'),
    path('api/topics/reorder/', views.api_reorder_topics, name='api_reorder_topics'),
    path('course/<int:course_id>/', views.course_detail_view, name='course_detail'),
    # Authentication URLs
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('toggle-active/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),

    # Password Reset URLs
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             form_class=StrictPasswordResetForm,
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             html_email_template_name='accounts/password_reset_email.html',  # 
             subject_template_name='accounts/password_reset_subject.txt',
             success_url='/accounts/password_reset/done/'  # Changed to absolute path
         ),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/reset/done/'  # Changed to absolute path
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    # AJAX validation endpoints
    path('ajax/check-username/', views.check_username, name='ajax_check_username'),
    path('ajax/check-email/', views.check_email, name='ajax_check_email'),
    path('ajax/check-student-number/', views.check_student_number, name='ajax_check_student_number'),
]