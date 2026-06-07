import json
from datetime import date, time

from Apps.appointments.models import Agenda
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

MESES_PT = (
    'Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
)

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


def client_dashboard(request):
    appointment = request.session.get('client_dashboard_appointment')
    return render(
        request,
        'dashboard/client_dashboard.html',
        {
            'appointment': appointment,
        },
    )


def parse_session_appointment(appointment):
    if not appointment:
        raise ValueError('Nenhum agendamento encontrado na session.')

    date_label = appointment.get('date')
    hour_label = appointment.get('hour')
    if not date_label or not hour_label:
        raise ValueError('Data ou horario atual nao encontrado na session.')

    day, month = date_label.split('/')
    hour, minute = hour_label.split(':')
    appointment_date = date(date.today().year, int(month), int(day))
    appointment_time = time(int(hour), int(minute))
    return appointment_date, appointment_time


def get_current_appointment_filter(request, appointment):
    appointment_date, appointment_time = parse_session_appointment(appointment)
    cliente_id = request.session.get('usuario_id')
    if not cliente_id:
        raise ValueError('Cliente nao identificado na session.')

    return {
        'clienteFk_id': cliente_id,
        'data': appointment_date,
        'hora': appointment_time,
        'status': Agenda.TipoStatus.CONFIRMADO,
    }


def is_slot_available(appointment_date, slot, current_filter):
    return not Agenda.objects.filter(
        data=appointment_date,
        hora=slot,
        status=Agenda.TipoStatus.CONFIRMADO,
    ).exclude(**current_filter).exists()


@require_GET
def reschedule_options(request):
    appointment = request.session.get('client_dashboard_appointment')
    try:
        appointment_date, appointment_time = parse_session_appointment(appointment)
        current_filter = get_current_appointment_filter(request, appointment)
    except ValueError as exc:
        return JsonResponse({'success': False, 'error': str(exc)}, status=400)

    slots = []
    for slot in AVAILABLE_SLOTS:
        if slot == appointment_time:
            continue

        if not is_slot_available(appointment_date, slot, current_filter):
            continue

        hour_label = slot.strftime('%H:%M')
        slots.append({
            'id': hour_label,
            'date': appointment['date'],
            'label': 'Disponivel',
            'hour': hour_label,
            'professional': appointment.get('professional', '-'),
        })

    return JsonResponse({'success': True, 'slots': slots})


def trabalhos_mes(request):
    trabalhos_mes = []

    agendas = Agenda.objects.filter(
        profissionalFk_id=request.session.get('usuario_id')#requisita os trabalhos do profissional
    )

    for agenda in agendas:

        servicos = []

        for agenda_servico in agenda.agenda_servicos.all():

            servicos.append(
                agenda_servico.servico.nome
            )

        trabalhos_mes.append({
            'data': agenda.data,
            'hora': agenda.hora,
            'cliente': agenda.clienteFk.nome,
            'servicos': ', '.join(servicos),
        })
    return trabalhos_mes


@require_POST
def remarcar(request):
    appointment = request.session.get('client_dashboard_appointment')
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON invalido'}, status=400)

    new_hour_label = str(payload.get('hour', '')).strip()
    try:
        appointment_date, _ = parse_session_appointment(appointment)
        current_filter = get_current_appointment_filter(request, appointment)
        hour, minute = new_hour_label.split(':')
        new_time = time(int(hour), int(minute))
    except (ValueError, TypeError) as exc:
        return JsonResponse({'success': False, 'error': str(exc)}, status=400)

    if new_time not in AVAILABLE_SLOTS:
        return JsonResponse(
            {'success': False, 'error': 'Horario fora da grade disponivel.'},
            status=400,
        )

    if not is_slot_available(appointment_date, new_time, current_filter):
        return JsonResponse(
            {'success': False, 'error': 'Este horario acabou de ser ocupado. Escolha outro horario.'},
            status=409,
        )

    updated_count = Agenda.objects.filter(**current_filter).update(hora=new_time)
    if updated_count == 0:
        return JsonResponse(
            {'success': False, 'error': 'Agendamento atual nao encontrado para remarcacao.'},
            status=404,
        )

    appointment['hour'] = new_time.strftime('%H:%M')
    appointment['status'] = 'confirmed'
    request.session['client_dashboard_appointment'] = appointment
    request.session.modified = True

    return JsonResponse({
        'success': True,
        'message': 'Atendimento remarcado com sucesso.',
        'appointment': appointment,
        'updated_count': updated_count,
    })


def professional_dashboard(request):
    hoje = date.today()
    mes_atual = MESES_PT[hoje.month - 1]

    return render(
        request,
        'dashboard/professional_dashboard.html',
        {
            'mes_atual': mes_atual,
            'trabalhos_mes': trabalhos_mes(request),
        },
    )


@require_POST
def cancelar_atendimento(request):
    appointment = request.session.get('client_dashboard_appointment')
    try:
        current_filter = get_current_appointment_filter(request, appointment)
    except ValueError as exc:
        return JsonResponse({'success': False, 'error': str(exc)}, status=400)

    updated_count = Agenda.objects.filter(**current_filter).update(
        status=Agenda.TipoStatus.CANCELADO,
    )
    if updated_count == 0:
        return JsonResponse(
            {'success': False, 'error': 'Agendamento atual nao encontrado para cancelamento.'},
            status=404,
        )

    appointment['status'] = 'canceled'
    request.session['client_dashboard_appointment'] = appointment
    request.session.modified = True

    return JsonResponse({
        'success': True,
        'message': 'Atendimento cancelado.',
        'appointment': appointment,
        'updated_count': updated_count,
    })
