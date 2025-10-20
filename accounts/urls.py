from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import UserViewSet, SkillViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('skills', SkillViewSet, basename='skill')

urlpatterns = [
    path('', include(router.urls)),
]
