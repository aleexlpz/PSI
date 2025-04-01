from django.db import models
from django.utils.timezone import now
from chess_models.constants import TournamentSpeed, TournamentBoardType, RankingSystem, TournamentType
from django.contrib.auth.models import User 

class Tournament(models.Model):
    
    name = models.CharField(
        max_length=128,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Nombre del torneo"
    )
    
    administrativeUser = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Usuario administrador"
    )
    
    players = models.ManyToManyField(
        'Player',
        through='tournamentPlayers',
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
        verbose_name="Tipo de torneo",
        choices=TournamentType.choices
    )
    
    tournament_speed = models.CharField(
        max_length=2,
        verbose_name="Velocidad del torneo",
        choices=TournamentSpeed.choices
    )
    
    board_type = models.CharField(
        max_length=3,
        verbose_name="Tipo de tablero",
        choices= TournamentBoardType.choices
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
    
    rankingList = models.ManyToManyField(
        'RankingSystemClass',  
        blank=True,
        verbose_name="Sistemas de clasificación asociados"
    )
    
    def getPlayers(self, sorted=False):
        """
        Devuelve los jugadores del torneo, opcionalmente ordenados según criterios.
        
        Args:
            sorted (bool): Si True, ordena según el tipo de torneo. Si False, 
                          devuelve en orden de inserción.
        
        Returns:
            QuerySet: Lista de jugadores, ordenados o no según parámetro.
        """
        if not sorted:
        # Orden por inscripción usando el modelo intermedio
            through_relations = TournamentPlayers.objects.filter(
                tournament=self
            ).order_by('registration_order')
            return [rel.player for rel in through_relations]
        else:
            # Lógica existente de ordenamiento por ratings
            if (self.tournament_speed == TournamentSpeed.RAPID and 
                self.board_type == TournamentBoardType.LICHESS):
                return list(self.players.order_by('-lichess_rating_rapid'))
            elif (self.tournament_speed == TournamentSpeed.BLITZ and 
                self.board_type == TournamentBoardType.LICHESS):
                return list(self.players.order_by('-lichess_rating_blitz'))
            elif (self.tournament_speed == TournamentSpeed.BULLET and 
                self.board_type == TournamentBoardType.LICHESS):
                return list(self.players.order_by('-lichess_rating_bullet'))
            elif self.board_type == TournamentBoardType.OTB:
                return list(self.players.order_by('-fide_rating'))
            else:
                return list(self.players.order_by('name'))
            
    def add_player(self, player):
        """
        Agrega un jugador al torneo y asigna un orden de inscripción.
        
        Args:
            player (Player): Instancia del jugador a agregar.
            
        Raises:
            ValueError: Si el jugador ya está inscrito en el torneo.
        """
        last_order = TournamentPlayers.objects.filter(
            tournament=self
        ).aggregate(models.Max('registration_order'))['registration_order__max'] or 0
        
        TournamentPlayers.objects.create(
            tournament=self,
            player=player,
            registration_order=last_order + 1
        )
        
    def getPlayersCount(self):
        """
        Devuelve el número de jugadores inscritos en el torneo.
        
        Returns:
            int: Número de jugadores inscritos.
        """
        return self.players.count()
    

class TournamentPlayers(models.Model):
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    registration_order = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['registration_order']
        unique_together = ('tournament', 'player')
        

class RankingSystemClass(models.Model ) :
    value = models.CharField(
        max_length=2,
        choices=RankingSystem.choices,
        primary_key=True
        )