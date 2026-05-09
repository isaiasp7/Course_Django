from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def select_day(request):
    return render(
        request,
        'appointments/select_day.html'
    )
def select_hour(request):
    return render(
        request,
        'appointments/select_hour.html'
    )
def confirm(request):
    return render(
        request,
        'appointments/confirm_appointment.html'
    )