from django.contrib import admin
from django.urls import path, include
from core import views as site
from core import views_forms as form_views
from accounts.views_html import signup, profile_detail, profile_edit
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # HTML pages
    path('', site.home, name='home'),
    path('feed/', site.feed, name='feed'),
    path('companies/', site.companies_list, name='companies_list'),
    path('companies/new/', form_views.company_create, name='company_create'),
    path('companies/<slug:slug>/', site.company_detail, name='company_detail'),
    path('companies/<slug:slug>/edit/', form_views.company_edit, name='company_edit'),

    path('jobs/', site.jobs_list, name='jobs_list'),
    path('jobs/new/', form_views.job_create, name='job_create'),
    path('jobs/<int:id>/', site.job_detail, name='job_detail'),
    path('jobs/<int:id>/edit/', form_views.job_edit, name='job_edit'),

    path('people/', site.users_list, name='users_list'),
    path('profile/<str:username>/', profile_detail, name='profile_detail'),
    path('profile/<str:username>/edit/', profile_edit, name='profile_edit'),
    path('connections/', include('connections.urls_html')),


    # CRUD
    path('posts/new/', form_views.post_create, name='post_create'),
    path('posts/<int:id>/edit/', form_views.post_edit, name='post_edit'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', csrf_exempt(auth_views.LogoutView.as_view(next_page='home')), name='logout'),
    path('signup/', signup, name='signup'),

    # Admin & API
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/companies/', include('companies.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/connections/', include('connections.urls')),
]
