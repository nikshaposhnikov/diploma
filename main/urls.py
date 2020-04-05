from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import never_cache
from learnDjango.urls import *

from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

app_name = 'main'

urlpatterns = [
    # Users urls
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register_teacher/done/', RegisterTeacherDoneView.as_view(), name='register_teacher_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/logout/', BBLogoutView.as_view(), name='logout'),
    path('accounts/change_password/', PasswordChangeView.as_view(), name='password_change'),
    path('accounts/reset_password/', BBPasswordResetView.as_view(form_class=EmailValidationOnForgotPassword),
         name='password_reset'),
    path('accounts/reset_password/done/', reset_password_done, name='reset_password_done'),
    path('accounts/change_password/done/', change_password_done, name='change_password_done'),
    path('accounts/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('accounts/login/', login_page, name='login'),
    path('accounts/change_comment/<int:group_pk>/<int:bb_pk>/<int:pk>/', comment_change, name='comment_change'),
    path('accounts/delete_comment/<int:group_pk>/<int:bb_pk>/<int:pk>/', comment_delete, name='comment_delete'),

    # Teacher functionality
    path('accounts/register/teacher/', RegisterTeacherView.as_view(), name='register_teacher'),
    path('accounts/profile/change/<int:pk>/', profile_bb_change, name='profile_bb_change'),
    path('accounts/profile/delete/<int:pk>/', profile_bb_delete, name='profile_bb_delete'),
    path('accounts/profile/add/', profile_bb_add, name='profile_bb_add'),
    path('accounts/profile/<int:pk>/', profile_bb_detail, name='profile_bb_detail'),
    path('accounts/profile/subject/<int:pk>/file/change/', profile_file_add, name='profile_file_add'),
    path('accounts/profile/subject/<int:pk>/', profile_sub_detail, name='profile_sub_detail'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/profile/subjects/', teacher_subjects, name='teacher_subjects'),
    path('list_schedule/', list_schedule, name='list_schedule'),
    path('list_schedule/detail_schedule/<int:pk>/', detail_schedule, name='detail_schedule'),
    path('accounts/profile/delete_teacher/', DeleteTeacherView.as_view(), name='profile_teacher_delete'),

    # Student functionality
    path('accounts/profile/student_subjects/', student_subjects, name='student_subjects'),
    path('accounts/profile/student_subject/<int:pk>/', student_sub_detail, name='student_sub_detail'),
    path('accounts/profile/student_schedule/', student_schedule, name='student_schedule'),
    path('accounts/student_profile/', student_profile, name='student_profile'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/profile/teacher_change/', ChangeTeacherInfoView.as_view(), name='profile_teacher_change'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),

    # General
    path('<int:group_pk>/<int:pk>/', detail, name='detail'),
    path('error_perm_teach/', error_perm_teach, name='error_perm_teach'),
    path('<int:pk>/', by_group, name='by_group'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index'),

]
