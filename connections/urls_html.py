from django.urls import path
from . import views_html

urlpatterns = [
    path('', views_html.connections_list, name='connections_list'),
    path('requests/', views_html.connection_requests, name='connection_requests'),
    path('add/<str:username>/', views_html.send_request, name='connection_add'),
    path('accept/<int:id>/', views_html.accept_request, name='connection_accept'),
    path('reject/<int:id>/', views_html.reject_request, name='connection_reject'),
    path('remove/<str:username>/', views_html.remove_connection, name='connection_remove'),
]
