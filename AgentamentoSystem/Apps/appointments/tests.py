from datetime import date, time

from django.test import TestCase

from Apps.accounts.models import Cliente, TipoUsuario
from Apps.appointments.models import Agenda
from Apps.appointments.services import delete_expired_agendas


class ExpiredAgendaCleanupTests(TestCase):
    def test_delete_expired_agendas_removes_past_slots(self):
        cliente = Cliente.objects.create(
            nome='Cliente',
            email='cliente@example.com',
            numero='11999999999',
            senha='x',
        )
        profissional = Cliente.objects.create(
            nome='Profissional',
            email='profissional@example.com',
            numero='11888888888',
            senha='x',
            tipo=TipoUsuario.PROFISSIONAL,
        )
        expired = Agenda.objects.create(
            data=date(2026, 6, 13),
            hora=time(8, 0),
            clienteFk=cliente,
            profissionalFk=profissional,
        )
        active = Agenda.objects.create(
            data=date(2026, 6, 13),
            hora=time(15, 0),
            clienteFk=cliente,
            profissionalFk=profissional,
        )

        delete_expired_agendas(
            today=date(2026, 6, 13),
            current_time=time(12, 0),
        )

        self.assertFalse(Agenda.objects.filter(pk=expired.pk).exists())
        self.assertTrue(Agenda.objects.filter(pk=active.pk).exists())
