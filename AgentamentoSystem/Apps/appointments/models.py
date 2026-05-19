from django.db import models
from Apps.accounts.models import Cliente

# Create your models here.
class Agenta(models.Model):
    data = models.DateField(null=False)
    hora = models.DateTimeField(null=False)
    servicoFK = models.ForeignKey(Cliente,null=False,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.data} - {self.hora}"
    
class Servicos(models.Model):
    preco = models.DecimalField(max_digits=4, decimal_places=2, null=False)
    nome = models.CharField(max_length=70, null=False)
    def __str__(self):
        return f"{self.nome}"