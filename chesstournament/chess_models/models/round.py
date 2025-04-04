from django.db import models
from django.core.exceptions import ValidationError
from .tournament import Tournament

class Round(models.Model):
    name = models.CharField(max_length=128, verbose_name="Nombre de la ronda")
    
    # Cambia related_name a 'round_set' para coincidir con los tests
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='game_set',
        verbose_name="Torneo asociado"
    )
    
    start_date = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=True,
        verbose_name="Fecha de inicio"
    )
    
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de finalización"
    )
    
    finish = models.BooleanField(
        default=False,
        verbose_name="¿Ronda finalizada?"
    )
    