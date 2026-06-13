from datetime import date, datetime

from django.db.models import Q

from Apps.appointments.models import Agenda


def delete_expired_agendas(today=None, current_time=None):
    today = today or date.today()
    current_time = current_time or datetime.now().time()

    return Agenda.objects.filter(
        Q(data__lt=today) | Q(data=today, hora__lt=current_time),
    ).delete()
