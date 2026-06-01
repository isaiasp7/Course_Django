from django.db import models

# Create your models here.
class TipoUsuario(models.TextChoices):
    CLIENTE = 'CLIENTE', 'Cliente'
    PROFISSIONAL = 'PROFISSIONAL', 'Profissional'


class Cliente(models.Model):
    nome = models.CharField(max_length=80)
    email = models.EmailField(max_length=100)
    numero = models.CharField(max_length=15)
    senha = models.CharField(max_length=100)

    tipo = models.CharField(
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.CLIENTE
    )
    def __str__(self):
        return f"{self.nome}"

