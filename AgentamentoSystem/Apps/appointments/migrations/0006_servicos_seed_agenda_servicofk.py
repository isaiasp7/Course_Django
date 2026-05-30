from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion

SERVICOS_INICIAIS = [
    ('Corte Moderno', Decimal('80.00')),
    ('Barba Premium', Decimal('50.00')),
    ('Tratamento Facial', Decimal('120.00')),
    ('Massagem Relaxante', Decimal('90.00')),
]


def criar_servicos_iniciais(apps, schema_editor):
    Servicos = apps.get_model('appointments', 'Servicos')
    for nome, preco in SERVICOS_INICIAIS:
        Servicos.objects.get_or_create(nome=nome, defaults={'preco': preco})


def vincular_servico_em_agendas(apps, schema_editor):
    Agenda = apps.get_model('appointments', 'Agenda')
    Servicos = apps.get_model('appointments', 'Servicos')
    servico_padrao = Servicos.objects.order_by('id').first()
    if not servico_padrao:
        return
    Agenda.objects.filter(servicoFK__isnull=True).update(servicoFK=servico_padrao)


def reverter_servicos_iniciais(apps, schema_editor):
    Servicos = apps.get_model('appointments', 'Servicos')
    nomes = [nome for nome, _ in SERVICOS_INICIAIS]
    Servicos.objects.filter(nome__in=nomes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0005_agenda_clientefk_hora_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicos',
            name='preco',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
        migrations.RunPython(criar_servicos_iniciais, reverter_servicos_iniciais),
        migrations.AddField(
            model_name='agenda',
            name='servicoFK',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='agendamentos',
                to='appointments.servicos',
            ),
        ),
        migrations.RunPython(vincular_servico_em_agendas, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='agenda',
            name='servicoFK',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='agendamentos',
                to='appointments.servicos',
            ),
        ),
    ]
