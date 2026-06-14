import json
from datetime import date, timedelta, time

from django.test import TestCase
from django.urls import reverse

from Apps.accounts.models import Cliente, TipoUsuario
from Apps.appointments.models import Agenda, AgendaServico, Servicos


class LoginRedirectTests(TestCase):
    def setUp(self):
        self.login_url = reverse('accounts:login')
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

    def post_login(self, email, password='x'):
        return self.client.post(
            self.login_url,
            data=json.dumps({
                'email': email,
                'password': password,
            }),
            content_type='application/json',
        )

    def test_client_without_confirmed_appointment_goes_to_select_day(self):
        response = self.post_login(self.client_user.email)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['next_url'], '/appointments/selectDay/')
        self.assertNotIn('client_dashboard_appointment', self.client.session)

    def test_client_with_confirmed_appointment_goes_to_dashboard(self):
        servico = Servicos.objects.create(nome='Corte', preco='50.00')
        agenda = Agenda.objects.create(
            data=date.today() + timedelta(days=1),
            hora=time(8, 0),
            clienteFk=self.client_user,
            profissionalFk=self.professional,
            status=Agenda.TipoStatus.CONFIRMADO,
        )
        AgendaServico.objects.create(agenda=agenda, servico=servico)

        response = self.post_login(self.client_user.email)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['next_url'], '/dashboard/')
        appointment = self.client.session['client_dashboard_appointment']
        self.assertEqual(appointment['agenda_id'], agenda.id)
        self.assertEqual(appointment['professional'], self.professional.nome)
        self.assertEqual(appointment['service'], 'Corte')

    def test_professional_login_still_goes_to_professional_dashboard(self):
        response = self.post_login(self.professional.email)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['next_url'], '/dashboard/profissional/')
