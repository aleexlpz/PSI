from django.db import models
from django.core.exceptions import ValidationError
from .tournament import Tournament


class Round(models.Model):
    """
    Modelo que representa una ronda en un torneo de ajedrez.
    Cada torneo puede tener múltiples rondas.
    """
    name = models.CharField(
        max_length=128, 
        verbose_name="Nombre de la ronda"
    )

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='rounds',
        verbose_name="Torneo"
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

    fnish = models.BooleanField(
        default=False,
        verbose_name="¿Ronda finalizada?"
    )

    