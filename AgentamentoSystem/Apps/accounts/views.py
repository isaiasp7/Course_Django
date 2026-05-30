from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Cliente
import json

def login(request):
    return render(request, 'accounts/login.html')
def validateLogin(request){
    if request.method=='POST':
        return Cliente.objects.filter(email=email, senha=senha).exists()?
    
}
def profile(request):
    return render(request, 'accounts/profile.html')

def register(request):
    if request.method == 'GET':
        return render(request, 'accounts/register.html')

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Validar dados
            nome = data.get('name', '').strip()
            email = data.get('email', '').strip()
            numero = data.get('phone', '').strip()
            senha = data.get('password', '').strip()

            if not all([nome, email, numero, senha]):
                return JsonResponse({'success': False, 'error': 'Todos os campos são obrigatórios'}, status=400)

            # Verificar se email já existe
            if Cliente.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'error': 'Este email já está cadastrado'}, status=400)

            # Criar novo cliente
            cliente = Cliente.objects.create(
                nome=nome,
                email=email,
                numero=numero,
                senha=senha
            )

            return JsonResponse({'success': True, 'message': f'Cadastro realizado com sucesso! Bem-vindo, {nome}!'})
          

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

