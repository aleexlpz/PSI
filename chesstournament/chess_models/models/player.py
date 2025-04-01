from django.db import models
from django.core.exceptions import ValidationError
import requests
from django.utils import timezone

class Player(models.Model):
    """
    Modelo que representa a un jugador de ajedrez en el sistema.
    Almacena información personal, perfiles en plataformas y clasificaciones.
    """
    id = models.IntegerField(
        primary_key=True,
        verbose_name="ID del jugador"
    )
    
    name = models.CharField(
        max_length=256,
        blank=True,
        verbose_name="Nombre del jugador"
    )

    email = models.EmailField(
        blank=True,
        verbose_name="Correo electrónico"
    )

    country = models.CharField(
        max_length=2,
        blank=True,
        verbose_name="País"
    )

    lichess_username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        verbose_name="Nombre de usuario en Lichess"
    )

    lichess_rating_bullet = models.IntegerField(
        default=0,
        verbose_name="Rating Bullet en Lichess"
    )

    lichess_rating_blitz = models.IntegerField(
        default=0,
        verbose_name="Rating Blitz en Lichess"
    )

    lichess_rating_rapid = models.IntegerField(
        default=0,
        verbose_name="Rating Rapid en Lichess"
    )

    lichess_rating_classical = models.IntegerField(
        default=0,
        verbose_name="Rating Classical en Lichess"
    )

    fide_id = models.IntegerField(
        unique=True,
        null=True,
        blank=True,
        verbose_name="ID FIDE"
    )

    fide_rating_blitz = models.IntegerField(
        default=0,
        verbose_name="Rating Blitz FIDE"
    )

    fide_rating_rapid = models.IntegerField(
        default=0,
        verbose_name="Rating Rapid FIDE"
    )

    fide_rating_classical = models.IntegerField(
        default=0,
        verbose_name="Rating Classical FIDE"
    )

    creation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    update_date = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )