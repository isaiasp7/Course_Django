from django.urls import path

from . import views


app_name = 'dashboard'

urlpatterns = [
    path('', views.client_dashboard, name='client_dashboard'),
    path('profissional/', views.professional_dashboard, name='professional_dashboard'),
    path('profissional/remarcar/opcoes/', views.professional_reschedule_options, name='professional_reschedule_options'),
    path('profissional/remarcar/', views.professional_remarcar, name='professional_remarcar'),
    path('remarcar/opcoes/', views.reschedule_options, name='reschedule_options'),
    path('remarcar/', views.remarcar, name='remarcar'),
    path('cancelar/', views.cancelar_atendimento, name='cancelar_atendimento'),
]
