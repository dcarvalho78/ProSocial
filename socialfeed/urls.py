from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import people_view, companies_view, jobs_view


urlpatterns = [
    path('api/notifications/archive/', views.notifications_archive, name='notifications_archive'),
    path('api/notifications/clear/', views.notifications_clear, name='notifications_clear'),
    path('', views.feed, name='feed'),
    path('api/posts/', views.api_posts, name='api_posts'),
    path('api/post/create/', views.create_post, name='create_post'),
    path('api/post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('api/post/<int:post_id>/likers/', views.likers_post, name='likers_post'),
    path('api/post/<int:post_id>/update/', views.update_post, name='post_update'),
    path('api/post/<int:post_id>/delete/', views.delete_post, name='post_delete'),
    path('api/post/<int:post_id>/repost/', views.repost_post, name='post_repost'),
    path('api/reply/create/', views.create_reply, name='create_reply'),
    path('api/reply/<int:reply_id>/like/', views.like_reply, name='like_reply'),
    path('api/follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/notifications/mark-read/', views.notifications_mark_read, name='notifications_mark_read'),
    path("jobs/filter/", views.filter_jobs_ajax, name="filter_jobs_ajax"),
    path('hashtag/<str:tag>/', views.hashtag, name='hashtag'),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('project/create/', views.project_create_view, name='project_create'),
    path('company/create/', views.company_create_view, name='company_create'),
    path('job/create/', views.job_create_view, name='job_create'),
    path('people/', people_view, name='people'),
    path("broadcast/<str:room>/", views.broadcast, name="live_broadcast"),
    path("watch/<str:room>/", views.watch, name="live_watch"),
    path('companies/', companies_view, name='companies'),
    path('company/<int:id>/', views.company_detail, name='company_detail'),
    path('jobs/', jobs_view, name='jobs'),
    path("jobs/apply/<int:job_id>/", views.apply_for_job, name="apply_for_job"),
    path("job/<int:job_id>/delete/", views.job_delete_view, name="job_delete"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
