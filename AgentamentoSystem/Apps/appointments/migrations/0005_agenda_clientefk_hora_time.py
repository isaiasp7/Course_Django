import datetime

from django.db import migrations, models
import django.db.models.deletion


def copiar_cliente_e_hora(apps, schema_editor):
    Agenda = apps.get_model('appointments', 'Agenda')
    for agenda in Agenda.objects.all():
        agenda.clienteFk_id = agenda.servicoFK_id
        if isinstance(agenda.hora, datetime.datetime):
            agenda.hora_nova = agenda.hora.time()
        else:
            agenda.hora_nova = agenda.hora
        agenda.save(update_fields=['clienteFk_id', 'hora_nova'])


def reverter_cliente_e_hora(apps, schema_editor):
    Agenda = apps.get_model('appointments', 'Agenda')
    for agenda in Agenda.objects.all():
        agenda.servicoFK_id = agenda.clienteFk_id
        if agenda.hora_nova:
            agenda.hora = datetime.datetime.combine(agenda.data, agenda.hora_nova)
        agenda.save(update_fields=['servicoFK_id', 'hora'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_profissional_senha'),
        ('appointments', '0004_agenda_delete_agenta'),
    ]

    operations = [
        migrations.AddField(
            model_name='agenda',
            name='clienteFk',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='agendamentos',
                to='accounts.cliente',
            ),
        ),
        migrations.AddField(
            model_name='agenda',
            name='hora_nova',
            field=models.TimeField(null=True),
        ),
        migrations.RunPython(copiar_cliente_e_hora, reverter_cliente_e_hora),
        migrations.RemoveField(
            model_name='agenda',
            name='hora',
        ),
        migrations.RemoveField(
            model_name='agenda',
            name='servicoFK',
        ),
        migrations.RenameField(
            model_name='agenda',
            old_name='hora_nova',
            new_name='hora',
        ),
        migrations.AlterField(
            model_name='agenda',
            name='clienteFk',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='agendamentos',
                to='accounts.cliente',
            ),
        ),
    ]
