from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from .models import Cliente

def login(request):
    userClient = Cliente.objects.all()
    return render(request,'accounts/login.html',{'userClient':userClient})
def profile(request):
    return render(request,'accounts/profile.html')
def register(request):
    return render(request,'accounts/register.html')

