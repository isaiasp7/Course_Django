from django.shortcuts import render
from Apps.appointments.models import Agenda
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
    if request.method == 'GET':
        return render(
            request,
            'appointments/confirm_appointment.html'
        )
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Você precisa buscar as instâncias relacionadas
            # servico = Servico.objects.get(id=data.get('servico_id'))  # Ajuste conforme seu modelo
            # profissional = Profissional.objects.get(id=data.get('profissional_id'))
            # cliente = Cliente.objects.get(id=data.get('cliente_id'))  # Ou use o usuário logado
            
            # Criar o agendamento
            agenda = Agenda.objects.create(
                data=data.get('date'),          # Vírgula aqui!
                hora=data.get('time'),          # Vírgula aqui! (e use 'time' não 'name')
                # servicoFK=servico,            # Passe a instância, não o ForeignKey
                # profissionalFK=profissional,
                # clienteFK=cliente,
            )
            
            return JsonResponse({'success': True, 'message': f'Agendamento realizado com sucesso!'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)