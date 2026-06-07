from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Apps.appointments'

    def ready(self):
        from django.db.models.signals import post_migrate

        from Apps.appointments.default_servicos import ensure_default_servicos

        def seed_servicos(sender, **kwargs):
            if sender.label != 'appointments':
                return
            ensure_default_servicos()

        post_migrate.connect(seed_servicos, sender=self)
