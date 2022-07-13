from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='api_index'),
    path('events/', views.process_event, name='api_process_event'),
]