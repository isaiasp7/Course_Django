from django.db import models

# Create your models here.
class Cliente(models.Model):
    nome =  models.CharField(max_length=80,null=False)
    email = models.EmailField(max_length=100,null=False)
    numero = models.CharField(max_length=15,null=False)
    senha = models.CharField(max_length=100, null=False)

    def __str__(self):
        return f"{self.nome}"

class Profissional(models.Model):
    nome =  models.CharField(max_length=80, null=False)
    email = models.EmailField(max_length=100,null=False)
    numero = models.CharField(max_length=15,null=False)
    senha = models.CharField(max_length=100, null=False, default='', blank=True)
    def __str__(self):
        return f"{self.nome}"
