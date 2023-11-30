from django.db import models

# Create your models here.
class Palabra(models.Model):
    nombre = models.CharField(max_length=50)

class URL(models.Model):
    palabra = models.ForeignKey(Palabra, on_delete=models.CASCADE)
    url = models.URLField()
    titulo = models.CharField(max_length=255)
    relevancia = models.IntegerField()