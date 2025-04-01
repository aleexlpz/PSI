from django.db import models
from django.utils.timezone import now

class Tournament(models.Model):
    
    id = models.IntegerField(
        primary_key=True,
        verbose_name="ID del torneo"
    )
    
    name = models.CharField(
        max_length=128,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Nombre del torneo"
    )
    
    administrativeUser = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Usuario administrador"
    )
    
    players = models.ManyToManyField(
        'Player',
        null=True,
        blank=True,
        verbose_name="Jugadores participantes"
    )
    
    referee = models.ForeignKey(
        'Referee',  
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Árbitro del torneo"
    )
    
    start_date = models.DateField(
        default=now,
        null=True,
        verbose_name="Fecha de inicio"
    )
    
    end_date = models.DateField(
        null=True,
        verbose_name="Fecha de finalización"
    )
    
    max_update_time = models.IntegerField(
        default=43200,
        verbose_name="Tiempo máximo para actualizar resultados (segundos)"
    )
    
    only_administrative = models.BooleanField(
        default=False,
        verbose_name="Solo el administrador puede modificar juegos"
    )
    
    tournament_type = models.CharField(
        max_length=2,
        verbose_name="Tipo de torneo"
        # choices=TOURNAMENT_TYPE_CHOICES
    )
    
    tournament_speed = models.CharField(
        max_length=2,
        verbose_name="Velocidad del torneo"
        # choices=TOURNAMENT_SPEED_CHOICES
    )
    
    board_type = models.CharField(
        max_length=3,
        verbose_name="Tipo de tablero"
        # choices=TOURNAMENT_BOARD_TYPE_CHOICES
    )
    
    win_points = models.FloatField(
        default=1.0,
        verbose_name="Puntos por victoria"
    )
    
    draw_points = models.FloatField(
        default=0.5,
        verbose_name="Puntos por empate"
    )
    
    lose_points = models.FloatField(
        default=0.0,
        verbose_name="Puntos por derrota"
    )
    
    timeControl = models.CharField(
        max_length=32,
        default='15+0',
        verbose_name="Control de tiempo"
    )
    
    number_of_rounds_for_swiss = models.IntegerField(
        default=0,
        verbose_name="Número de rondas para torneos suizos"
    )