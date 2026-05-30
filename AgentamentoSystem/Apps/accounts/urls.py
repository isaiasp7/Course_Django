from django.urls import path
from . import views

app_name = 'accounts'


urlpatterns = [

    path(
        'login/',
        views.login,
        name='login'
    ),

    path(
        'perfil/',
        views.profile,
        name='perfil'
    ),
    path(
        'cadastro/',
        views.register,
        name='cadastro'
    ),
    path(
        'profissional/codigo/',
        views.professional_code,
        name='professional_code'
    ),
    path(
        'profissional/indisponibilidade/',
        views.professional_unavailable_days,
        name='professional_unavailable_days'
    ),

]
