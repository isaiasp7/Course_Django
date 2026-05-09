from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def login(request):
    return render(request,'index.html')
def tela_agendamentoDia(request):
    return render(request,'index.html')
def tela_agendamentoHorario(request):
    return render(request,'index.html')
def tela_selectService(request):
    return render(request,'index.html')
