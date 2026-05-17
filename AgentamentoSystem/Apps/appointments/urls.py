from django.urls import path
from . import views

app_name = 'appointments'


urlpatterns = [

    path(
        'selectDay/',
        views.select_day,
        name='select_day'
    ),

    path(
        'selectHour/',
        views.select_hour,
        name='select_hour'
    ),
    path(
        'confirmAppoint/',
        views.confirm,
        name='confirmAppoint'
    ),

]