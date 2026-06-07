import json
import random
import re
from datetime import date, time

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from decimal import Decimal, InvalidOperation

from Apps.accounts.models import Cliente
from Apps.appointments.models import Agenda, AgendaServico, Servicos

AVAILABLE_SLOTS = [
    time(8, 0),
    time(8, 30),
    time(9, 0),
    time(9, 30),
    time(10, 0),
    time(10, 30),
    time(11, 0),
    time(14, 0),
    time(14, 30),
    time(15, 0),
    time(15, 30),
    time(16, 0),
    time(16, 30),
    time(17, 0),
    time(17, 30),
    time(18, 0),
]
AVAILABLE_SLOT_LABELS = [slot.strftime('%H:%M') for slot in AVAILABLE_SLOTS]

MESES_PT = {
    'janeiro': 1,
    'fevereiro': 2,
    'marco': 3,
    'abril': 4,
    'maio': 5,
    'junho': 6,
    'julho': 7,
    'agosto': 8,
    'setembro': 9,
    'outubro': 10,
    'novembro': 11,
    'dezembro': 12,
}

MONTH_KEYS = {
    5: 'may',
    6: 'june',
}


def build_booked_slots_by_day():
    booked_slots_by_day = {}
    agendas = Agenda.objects.filter(
        hora__in=AVAILABLE_SLOTS,
        data__year=date.today().year,
        data__month__in=MONTH_KEYS.keys(),
        status=Agenda.TipoStatus.CONFIRMADO,
    ).values_list('data', 'hora')

    for agenda_date, agenda_time in agendas:
        month_key = MONTH_KEYS.get(agenda_date.month)
        if not month_key:
            continue

        day_key = f'{agenda_date.day}_{month_key}'
        booked_slots_by_day.setdefault(day_key, set()).add(
            agenda_time.strftime('%H:%M'),
        )

    return {
        day_key: sorted(slots)
        for day_key, slots in booked_slots_by_day.items()
    }


def get_fully_booked_days(booked_slots_by_day):
    available_slots = set(AVAILABLE_SLOT_LABELS)
    return [
        day_key
        for day_key, booked_slots in booked_slots_by_day.items()
        if available_slots.issubset(set(booked_slots))
    ]


def select_day(request):
    booked_slots_by_day = build_booked_slots_by_day()
    fully_booked_days = get_fully_booked_days(booked_slots_by_day)
    return render(
        request,
        'appointments/select_day.html',
        {
            'fully_booked_days': fully_booked_days,
            'fully_booked_days_json': json.dumps(fully_booked_days),
        },
    )


def select_hour(request):
    booked_slots_by_day = build_booked_slots_by_day()
    return render(
        request,
        'appointments/select_hour.html',
        {
            'available_slots': AVAILABLE_SLOT_LABELS,
            'available_slots_json': json.dumps(AVAILABLE_SLOT_LABELS),
            'booked_slots_by_day': booked_slots_by_day,
            'booked_slots_by_day_json': json.dumps(booked_slots_by_day),
            'selected_date': request.GET.get('date', ''),
        },
    )


def parse_appointment_date_time(date_label, time_label):
    """
    Converte labels da UI (ex: '27 de Maio', '14:30') em date e time.
    """
    if not date_label or not time_label:
        raise ValueError('Data e horario sao obrigatorios')

    date_match = re.match(
        r'^(\d{1,2})\s+de\s+([A-Za-zÀ-ú]+)$',
        date_label.strip(),
        re.IGNORECASE,
    )
    if not date_match:
        raise ValueError('Formato de data invalido')

    day = int(date_match.group(1))
    month_name = date_match.group(2).lower()
    month = MESES_PT.get(month_name)
    if not month:
        raise ValueError('Mes invalido')

    time_match = re.match(r'^(\d{1,2}):(\d{2})$', time_label.strip())
    if not time_match:
        raise ValueError('Formato de horario invalido')

    hour = int(time_match.group(1))
    minute = int(time_match.group(2))
    year = date.today().year

    appointment_date = date(year, month, day)
    appointment_time = time(hour, minute)
    return appointment_date, appointment_time


def resolve_servicos(services_payload):
    servicos = []
    for item in services_payload:
        if not isinstance(item, dict):
            continue

        servico_id = item.get('id')
        if servico_id:
            try:
                servicos.append(Servicos.objects.get(pk=servico_id))
                continue
            except (Servicos.DoesNotExist, ValueError, TypeError):
                pass

        nome = str(item.get('name', '')).strip()
        if not nome:
            continue

        preco_raw = item.get('price', 0)
        try:
            preco = Decimal(str(preco_raw))
        except (InvalidOperation, TypeError):
            preco = Decimal('0')

        servico, _ = Servicos.objects.get_or_create(
            nome=nome,
            defaults={'preco': preco},
        )
        servicos.append(servico)

    return servicos


@require_http_methods(['GET', 'POST'])
def confirm(request):
    if request.method == 'GET':
        return render(
            request,
            'appointments/confirm_appointment.html',
            {'servicos': Servicos.objects.all().order_by('nome')},
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {'success': False, 'error': 'JSON invalido'},
            status=400,
        )

    date_label = data.get('date', '').strip()
    time_label = data.get('time', '').strip()
    cliente_email = data.get('cliente_email', '').strip()

    if not cliente_email:
        return JsonResponse(
            {'success': False, 'error': 'Cliente nao identificado. Faca login novamente.'},
            status=400,
        )

    try:
        cliente = Cliente.objects.get(email=cliente_email)
    except Cliente.DoesNotExist:
        return JsonResponse(
            {'success': False, 'error': 'Cliente nao encontrado para este e-mail.'},
            status=404,
        )


    profissionais = list(Cliente.objects.filter(tipo='profissional'))

    profissionais = list(Cliente.objects.filter(tipo='PROFISSIONAL'))

    if not profissionais:
        return JsonResponse(
            {'success': False, 'error': 'Nenhum profissional cadastrado no sistema.'},
            status=400,
        )

    profissional = random.choice(profissionais)

    services_payload = data.get('services', [])
    servicos = resolve_servicos(services_payload)
    if not servicos:
        return JsonResponse(
            {'success': False, 'error': 'Selecione pelo menos um servico valido.'},
            status=400,
        )

    try:
        appointment_date, appointment_time = parse_appointment_date_time(
            date_label,
            time_label,
        )
    except ValueError as exc:
        return JsonResponse(
            {'success': False, 'error': str(exc)},
            status=400,
        )

    if appointment_time not in AVAILABLE_SLOTS:
        return JsonResponse(
            {'success': False, 'error': 'Horario fora da grade disponivel.'},
            status=400,
        )

    if Agenda.objects.filter(
        data=appointment_date,
        hora=appointment_time,
        status=Agenda.TipoStatus.CONFIRMADO,
    ).exists():
        return JsonResponse(
            {'success': False, 'error': 'Este horario acabou de ser ocupado. Escolha outro horario.'},
            status=409,
        )

    agenda = Agenda.objects.create(
        data=appointment_date,
        hora=appointment_time,
        clienteFk=cliente,
        profissionalFk=profissional,
    )

    for servico in servicos:
        AgendaServico.objects.create(
            agenda=agenda,
            servico=servico,
        )

    servicos_nomes = [servico.nome for servico in servicos]
    request.session['usuario_id'] = cliente.id
    request.session['client_dashboard_appointment'] = {
        'agenda_id': agenda.id,
        'professional': profissional.nome,
        'service': ', '.join(servicos_nomes),
        'date': appointment_date.strftime('%d/%m'),
        'hour': appointment_time.strftime('%H:%M'),
        'duration': '30 minutos',
        'location': 'Presencial',
        'unit': 'Studio Centro',
        'status': 'confirmed',
    }
    request.session.modified = True

    return JsonResponse({
        'success': True,
        'message': 'Agendamento realizado com sucesso!',
        'agenda_id': agenda.id,
        'profissional_nome': profissional.nome,
        'servicos_nomes': servicos_nomes,
        'date': date_label,
        'time': time_label,
    })
