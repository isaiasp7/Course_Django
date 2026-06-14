import json
import secrets

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from Apps.appointments.models import Agenda
from Apps.appointments.services import delete_expired_agendas

from .middleware import SESSION_NAV_TOKEN, build_guest_url
from .models import Cliente, TipoUsuario

PROFESSIONAL_ACCESS_CODE = 'STUDIO-PRO-2026'
SESSION_REGISTER_TYPE = 'tipo_cadastro'


def get_next_confirmed_appointment(cliente):
    return (
        Agenda.objects.filter(
            clienteFk=cliente,
            status=Agenda.TipoStatus.CONFIRMADO,
        )
        .select_related('profissionalFk')
        .prefetch_related('agenda_servicos__servico')
        .order_by('data', 'hora', 'id')
        .first()
    )


def build_client_dashboard_appointment(agenda):
    servicos = [
        agenda_servico.servico.nome
        for agenda_servico in agenda.agenda_servicos.all()
    ]
    return {
        'agenda_id': agenda.id,
        'professional': agenda.profissionalFk.nome,
        'service': ', '.join(servicos),
        'date': agenda.data.strftime('%d/%m'),
        'hour': agenda.hora.strftime('%H:%M'),
        'duration': '30 minutos',
        'location': 'Presencial',
        'unit': 'Studio Centro',
        'status': 'confirmed',
    }


def login(request):
    if request.method == 'POST':
        try:
            delete_expired_agendas()
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            senha = data.get('password', '').strip()
            cliente = Cliente.objects.get(email=email, senha=senha)
            next_url = (
                '/dashboard/profissional/'
                if cliente.tipo == TipoUsuario.PROFISSIONAL
                else '/appointments/selectDay/'
            )
            existing_appointment = None

            if cliente.tipo == TipoUsuario.CLIENTE:
                existing_appointment = get_next_confirmed_appointment(cliente)
                if existing_appointment:
                    next_url = '/dashboard/'

            request.session['usuario_id'] = cliente.id
            request.session['usuario_nome'] = cliente.nome
            request.session['usuario_tipo'] = cliente.tipo
            if existing_appointment:
                request.session['client_dashboard_appointment'] = build_client_dashboard_appointment(
                    existing_appointment,
                )
            else:
                request.session.pop('client_dashboard_appointment', None)
            request.session.pop(SESSION_REGISTER_TYPE, None)
            return JsonResponse({
                'success': True,
                'email': cliente.email,
                'user_type': cliente.tipo,
                'next_url': next_url,
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON invalido'}, status=400)
        except Cliente.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'E-mail ou senha incorretos'}, status=401)

    request.session.flush()
    nav_token = secrets.token_urlsafe(16)
    request.session[SESSION_NAV_TOKEN] = nav_token
    return render(request, 'accounts/login.html', {'guest_nav_token': nav_token})


def profile(request):
    return render(request, 'accounts/profile.html')


def professional_code(request):
    error = None

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        if code == PROFESSIONAL_ACCESS_CODE:
            request.session[SESSION_REGISTER_TYPE] = 'profissional'
            nav_token = request.session.get(SESSION_NAV_TOKEN, '')
            return redirect(build_guest_url('accounts:cadastro', nav_token))
        error = 'Codigo invalido. Verifique com o administrador do studio.'

    return render(
        request,
        'accounts/professional_code.html',
        {
            'error': error,
            'guest_nav_token': request.session.get(SESSION_NAV_TOKEN, ''),
        },
    )


def register(request):
    account_type = request.session.get(SESSION_REGISTER_TYPE, 'cliente')

    if request.method == 'GET':
        return render(
            request,
            'accounts/register.html',
            {
                'account_type': account_type,
                'guest_nav_token': request.session.get(SESSION_NAV_TOKEN, ''),
            },
        )

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nome = data.get('name', '').strip()
            email = data.get('email', '').strip()
            numero = data.get('phone', '').strip()
            senha = data.get('password', '').strip()

            if not all([nome, email, numero, senha]):
                return JsonResponse({'success': False, 'error': 'Todos os campos sao obrigatorios'}, status=400)

            if account_type == 'profissional':
                profissional = create_professional_object(nome, email, numero, senha)
                if profissional:
                    return JsonResponse({
                        'success': True,
                        'message': f'Cadastro profissional realizado com sucesso, {profissional.nome}!',
                        'next_url': '/accounts/profissional/indisponibilidade/',
                    })
                return JsonResponse({'success': False, 'error': 'Email ja cadastrado'}, status=400)

            cliente = create_client_object(nome, email, numero, senha)
            if cliente:
                return JsonResponse({
                    'success': True,
                    'message': f'Cadastro realizado com sucesso! Bem-vindo, {cliente.nome}!',
                    'next_url': '/accounts/login/',
                })
            return JsonResponse({'success': False, 'error': 'Email ja cadastrado'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON invalido'}, status=400)
        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)

    return JsonResponse({'success': False, 'error': 'Metodo nao permitido'}, status=405)


def create_client_object(nome, email, numero, senha):
    if Cliente.objects.filter(email=email).exists():
        return None

    cliente = Cliente.objects.create(
        nome=nome,
        email=email,
        numero=numero,
        senha=senha,
        tipo=TipoUsuario.CLIENTE,
    )
    return cliente


def create_professional_object(nome, email, numero, senha):
    if Cliente.objects.filter(email=email).exists():
        return None

    profissional = Cliente.objects.create(
        nome=nome,
        email=email,
        numero=numero,
        senha=senha,
        tipo=TipoUsuario.PROFISSIONAL,
    )
    return profissional
