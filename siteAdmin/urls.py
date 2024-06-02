from django.conf.urls.static import static
from django.urls import path

from AdminSkyLang import settings
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),

    path('courses/', views.courses, name='courses'),
    path('course/create/', views.create_course, name='create_course'),
    path('course/<int:course_id>/', views.course, name='course'),
    path('course/<int:course_id>/update/', views.update_course, name='update_course'),
    path('course/<int:course_id>/delete/', views.delete_course, name='delete_course'),

    path('comments/', views.comments, name='comments'),
    path('comment/create/', views.create_comment, name='create_comment'),
    path('comment/<int:comment_id>/', views.comment, name='comment'),
    path('comment/<int:comment_id>/update/', views.update_comment, name='update_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    path('exercises/', views.exercises, name='exercises'),
    path('exercise/create/', views.create_exercise, name='create_exercise'),
    path('exercise/<int:exercise_id>/', views.get_exercise, name='exercise'),
    path('exercise/<int:exercise_id>/update/', views.update_exercise, name='update_exercise'),
    path('exercise/<int:exercise_id>/delete/', views.delete_exercise, name='delete_exercise'),

    path('lectures/', views.lectures, name='lectures'),
    path('lecture/create/', views.create_lecture, name='create_lecture'),
    path('lecture/<int:lecture_id>/', views.get_lecture, name='lecture'),
    path('lecture/<int:lecture_id>/update/', views.update_lecture, name='update_lecture'),
    path('lecture/<int:lecture_id>/delete/', views.delete_lecture, name='delete_lecture'),

    path('users/', views.users, name='users'),
    path('user/create/', views.create_user, name='create_user'),
    path('user/<int:user_id>/', views.get_user, name='user'),
    path('user/<int:user_id>/update/', views.update_user, name='update_user'),
    path('user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
