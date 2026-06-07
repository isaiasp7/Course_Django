from django.db import migrations


def seed_servicos(apps, schema_editor):
    from Apps.appointments.default_servicos import SERVICOS_PADRAO

    Servicos = apps.get_model('appointments', 'Servicos')
    for nome, preco in SERVICOS_PADRAO:
        Servicos.objects.get_or_create(nome=nome, defaults={'preco': preco})


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0002_agenda_status'),
    ]

    operations = [
        migrations.RunPython(seed_servicos, migrations.RunPython.noop),
    ]
