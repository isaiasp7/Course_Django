from datetime import date

from django.shortcuts import render

MESES_PT = (
    'Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
)


def client_dashboard(request):
    return render(request, 'dashboard/client_dashboard.html')


def professional_dashboard(request):
    hoje = date.today()
    mes_atual = MESES_PT[hoje.month - 1]

    trabalhos_mes = [
        {
            'data': f'05/{hoje.month:02d}',
            'hora': '09:00',
            'cliente': 'Ana Silva',
            'servico': 'Corte e finalizacao',
        },
        {
            'data': f'12/{hoje.month:02d}',
            'hora': '14:30',
            'cliente': 'Carlos Mendes',
            'servico': 'Barba completa',
        },
        {
            'data': f'18/{hoje.month:02d}',
            'hora': '10:00',
            'cliente': 'Julia Costa',
            'servico': 'Coloracao',
        },
        {
            'data': f'22/{hoje.month:02d}',
            'hora': '16:00',
            'cliente': 'Pedro Lima',
            'servico': 'Corte masculino',
        },
        {
            'data': f'27/{hoje.month:02d}',
            'hora': '11:30',
            'cliente': 'Mariana Souza',
            'servico': 'Hidratacao',
        },
    ]

    return render(
        request,
        'dashboard/professional_dashboard.html',
        {
            'mes_atual': mes_atual,
            'trabalhos_mes': trabalhos_mes,
        },
    )
