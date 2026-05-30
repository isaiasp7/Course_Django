from django.db import models

from Apps.accounts.models import Cliente, Profissional


class Servicos(models.Model):
    nome = models.CharField(max_length=70, null=False)
    preco = models.DecimalField(max_digits=6, decimal_places=2, null=False)

    class Meta:
        verbose_name = 'Servico'
        verbose_name_plural = 'Servicos'

    def __str__(self):
        return f"{self.nome}"


class Agenda(models.Model):
    data = models.DateField(null=False)
    hora = models.TimeField(null=False)
    clienteFk = models.ForeignKey(
        Cliente,
        null=False,
        on_delete=models.CASCADE,
        related_name='agendamentos',
    )
    profissionalFk = models.ForeignKey(
        Profissional,
        null=False,
        on_delete=models.CASCADE,
        related_name='agendamentos_profissional',
    )

    def __str__(self):
        return f"{self.data} {self.hora}"


class AgendaServico(models.Model):
    agenda = models.ForeignKey(
        Agenda,
        null=False,
        on_delete=models.CASCADE,
        related_name='agenda_servicos',
        db_column='agenda_id',
    )
    servico = models.ForeignKey(
        Servicos,
        null=False,
        on_delete=models.CASCADE,
        related_name='agenda_servicos',
        db_column='servico_id',
    )

    class Meta:
        db_table = 'AgendaServico'
        verbose_name = 'Agenda servico'
        verbose_name_plural = 'Agenda servicos'

    def __str__(self):
        return f"Agenda {self.agenda_id} - {self.servico.nome}"
