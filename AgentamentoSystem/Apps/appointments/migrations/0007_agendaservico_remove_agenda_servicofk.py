import django.db.models.deletion
from django.db import migrations, models


def migrar_servicos_para_tabela_intermediaria(apps, schema_editor):
    Agenda = apps.get_model('appointments', 'Agenda')
    AgendaServico = apps.get_model('appointments', 'AgendaServico')

    for agenda in Agenda.objects.exclude(servicoFK__isnull=True):
        AgendaServico.objects.get_or_create(
            agenda_id=agenda.id,
            servico_id=agenda.servicoFK_id,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0006_servicos_seed_agenda_servicofk'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgendaServico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agenda', models.ForeignKey(db_column='agenda_id', on_delete=django.db.models.deletion.CASCADE, related_name='agenda_servicos', to='appointments.agenda')),
                ('servico', models.ForeignKey(db_column='servico_id', on_delete=django.db.models.deletion.CASCADE, related_name='agenda_servicos', to='appointments.servicos')),
            ],
            options={
                'verbose_name': 'Agenda servico',
                'verbose_name_plural': 'Agenda servicos',
                'db_table': 'AgendaServico',
            },
        ),
        migrations.RunPython(
            migrar_servicos_para_tabela_intermediaria,
            migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name='agenda',
            name='servicoFK',
        ),
    ]
