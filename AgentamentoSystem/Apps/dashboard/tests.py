import json
from datetime import date, timedelta, time

from django.test import Client, TestCase
from django.urls import reverse

from Apps.accounts.models import Cliente, TipoUsuario
from Apps.appointments.models import Agenda


class ProfessionalRescheduleTests(TestCase):
    def setUp(self):
        self.client_user = Cliente.objects.create(
            nome='Cliente',
            email='cliente@example.com',
            numero='11999999999',
            senha='x',
        )
        self.professional = Cliente.objects.create(
            nome='Profissional',
            email='profissional@example.com',
            numero='11888888888',
            senha='x',
            tipo=TipoUsuario.PROFISSIONAL,
        )
        self.agenda = Agenda.objects.create(
            data=date.today() + timedelta(days=1),
            hora=time(8, 0),
            clienteFk=self.client_user,
            profissionalFk=self.professional,
        )
        self.client = Client()
        session = self.client.session
        session['usuario_id'] = self.professional.id
        session['usuario_tipo'] = TipoUsuario.PROFISSIONAL
        session.save()

    def test_professional_can_reschedule_own_agenda(self):
        response = self.client.post(
            reverse('dashboard:professional_remarcar'),
            data=json.dumps({
                'agenda_id': self.agenda.id,
                'hour': '08:30',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.agenda.refresh_from_db()
        self.assertEqual(self.agenda.hora, time(8, 30))
        self.assertTrue(response.json()['success'])
        self.assertEqual(
            response.json()['appointment']['data_iso'],
            self.agenda.data.isoformat(),
        )

    def test_professional_dashboard_lists_agendas_by_date_and_hour(self):
        later_agenda = Agenda.objects.create(
            data=date.today() + timedelta(days=1),
            hora=time(15, 0),
            clienteFk=self.client_user,
            profissionalFk=self.professional,
        )

        response = self.client.get(reverse('dashboard:professional_dashboard'))

        self.assertEqual(response.status_code, 200)
        trabalhos = response.context['trabalhos_mes']
        self.assertEqual(
            [trabalho['id'] for trabalho in trabalhos],
            [self.agenda.id, later_agenda.id],
        )
        self.assertEqual(
            response.context['dias_trabalho'][0]['trabalhos'][0]['id'],
            self.agenda.id,
        )
