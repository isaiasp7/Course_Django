import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import Cliente, Profissional


PROFESSIONAL_ACCESS_CODE = 'STUDIO-PRO-2026'


def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            senha = data.get('password', '').strip()
            cliente = Cliente.objects.get(email=email, senha=senha)
            return JsonResponse({'success': True, 'email': cliente.email})
        except json.JSONDecodeError:
            return JsonResponse(
                {'success': False, 'error': 'JSON invalido'},
                status=400,
            )
        except Cliente.DoesNotExist:
            return JsonResponse(
                {'success': False, 'error': 'E-mail ou senha incorretos'},
                status=401,
            )

    return render(request, 'accounts/login.html')


def profile(request):
    return render(request, 'accounts/profile.html')


def professional_code(request):
    error = None

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        if code == PROFESSIONAL_ACCESS_CODE:
            cadastro_url = reverse('accounts:cadastro')
            return redirect(
                f'{cadastro_url}?tipo=profissional&codigo={PROFESSIONAL_ACCESS_CODE}'
            )
        error = 'Codigo invalido. Verifique com o administrador do studio.'

    return render(
        request,
        'accounts/professional_code.html',
        {'error': error},
    )


def professional_unavailable_days(request):
    return render(request, 'accounts/professional_unavailable_days.html')


def register(request):
    account_type = request.GET.get('tipo', 'cliente')
    professional_code_value = request.GET.get('codigo', '')
    is_professional = (
        account_type == 'profissional'
        and professional_code_value == PROFESSIONAL_ACCESS_CODE
    )

    if request.method == 'GET':
        return render(
            request,
            'accounts/register.html',
            {
                'account_type': 'profissional' if is_professional else 'cliente',
                'professional_code_value': professional_code_value if is_professional else '',
            },
        )

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nome = data.get('name', '').strip()
            email = data.get('email', '').strip()
            numero = data.get('phone', '').strip()
            senha = data.get('password', '').strip()
            requested_type = data.get('accountType', 'cliente')
            submitted_code = data.get('professionalCode', '').strip()

            if not all([nome, email, numero, senha]):
                return JsonResponse(
                    {'success': False, 'error': 'Todos os campos sao obrigatorios'},
                    status=400,
                )

            if requested_type == 'profissional':
                return create_professional(nome, email, numero, senha, submitted_code)

            return create_client(nome, email, numero, senha)

        except json.JSONDecodeError:
            return JsonResponse(
                {'success': False, 'error': 'JSON invalido'},
                status=400,
            )
        except Exception as exc:
            return JsonResponse(
                {'success': False, 'error': str(exc)},
                status=500,
            )

    return JsonResponse(
        {'success': False, 'error': 'Metodo nao permitido'},
        status=405,
    )


def create_client(nome, email, numero, senha):
    if Cliente.objects.filter(email=email).exists():
        return JsonResponse(
            {'success': False, 'error': 'Este email ja esta cadastrado'},
            status=400,
        )

    cliente = Cliente.objects.create(
        nome=nome,
        email=email,
        numero=numero,
        senha=senha,
    )

    return JsonResponse({
        'success': True,
        'message': f'Cadastro realizado com sucesso! Bem-vindo, {cliente.nome}!',
        'next_url': '/accounts/login/',
    })


def create_professional(nome, email, numero, senha, submitted_code):
    if submitted_code != PROFESSIONAL_ACCESS_CODE:
        return JsonResponse(
            {'success': False, 'error': 'Codigo profissional invalido'},
            status=403,
        )

    if Profissional.objects.filter(email=email).exists():
        return JsonResponse(
            {'success': False, 'error': 'Este email ja esta cadastrado como profissional'},
            status=400,
        )

    profissional = Profissional.objects.create(
        nome=nome,
        email=email,
        numero=numero,
        senha=senha,
    )

    return JsonResponse({
        'success': True,
        'message': f'Cadastro profissional realizado com sucesso, {profissional.nome}!',
        'next_url': '/accounts/profissional/indisponibilidade/',
    })
