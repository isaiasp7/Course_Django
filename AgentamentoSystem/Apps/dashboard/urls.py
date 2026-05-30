from django.urls import path

from . import views


app_name = 'dashboard'

urlpatterns = [
    path('', views.client_dashboard, name='client_dashboard'),
    path('profissional/', views.professional_dashboard, name='professional_dashboard'),
]
