from django.db import models
from django.utils.timezone import now
from chess_models.constants import TournamentSpeed, TournamentBoardType, RankingSystem, TournamentType
from django.contrib.auth.models import User 
import datetime as daytime

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
        through='TournamentPlayers',
        through_fields=('tournament', 'player'),
        related_name='tournaments'
    )
    
    referee = models.ForeignKey(
        'Referee',  
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Árbitro del torneo"
    )
    
    start_date = models.DateField(
        default=daytime.date.today,
        null=True,
        verbose_name="Fecha de inicio"
    )
    
    end_date = models.DateField(
        default=daytime.date.today,
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
        verbose_name="Número de rondas para torneos swiss"
    )
    
    rankingList = models.ManyToManyField(
        'RankingSystemClass',  
        #through='RankingSystemClass',
        blank=True,
        related_name="rounds",
        verbose_name="Sistemas de clasificación asociados"
    )

    def getPlayers(self, sorted=False, lichess_usernames=None):
        """
        Devuelve los jugadores del torneo, opcionalmente ordenados según criterios.
        
        Args:
            sorted (bool): Si True, ordena según el tipo de torneo. Si False, 
                        devuelve en orden de inserción.
            lichess_usernames (list): Lista de nombres de usuario de los jugadores,
                                    en caso de que necesites forzar un orden específico.
        
        Returns:
            QuerySet: Lista de jugadores, ordenados o no según parámetro.
        """
        if not sorted:
            through_relations = TournamentPlayers.objects.filter(
                tournament=self
            ).order_by('registration_order')
            players = [rel.player for rel in through_relations]

            return players
        else:
            if (self.tournament_speed == TournamentSpeed.RAPID and 
                self.board_type == TournamentBoardType.LICHESS):
                return list(self.players.order_by('-lichess_rating_rapid'))
            elif (self.tournament_speed == TournamentSpeed.BLITZ and 
                self.board_type == TournamentBoardType.LICHESS):
                return list(self.players.order_by('-lichess_rating_blitz'))
            elif (self.tournament_speed == TournamentSpeed.BULLET and 
                self.board_type == TournamentBoardType.LICHESS):
                return list(self.players.order_by('-lichess_rating_bullet'))
            elif (self.tournament_speed == TournamentSpeed.CLASSICAL and
                self.board_type == TournamentBoardType.LICHESS):
                return list(self.players.order_by('-lichess_rating_classical'))
            else:
                return list(self.players.order_by('name'))
        
    def getPlayersCount(self):
        """
        Devuelve el número de jugadores inscritos en el torneo.
        
        Returns:
            int: Número de jugadores inscritos.
        """
        return self.players.count()
    
    def cleanRankingList(self):
        """Limpia el campo rankingList del torneo"""
        self.rankingList.clear()
        
    
    def addToRankingList(self, ranking_value):
        """
        Añade un objeto RankingSystem al rankingList del torneo.
        Si no existe, lo crea primero.
        """
        ranking_obj, created = RankingSystemClass.objects.get_or_create(
            value=ranking_value
        )
        self.rankingList.add(ranking_obj)
    
    def getRoundCount(self):
        """Devuelve el número de rondas que tiene el torneo"""
        return self.round_set.count()

    def get_number_of_rounds_with_games(self):
        """Devuelve el número de rondas con al menos una partida jugada"""
        return self.round_set.filter(game__finished=True).distinct().count()

    def get_latest_round_with_games(self):
        """Devuelve la última ronda con partidas jugadas"""
        return self.round_set.filter(game__finished=True).order_by('-start_date').first()
    
    def removeFromRankingList(self, ranking_value):
        """
        Elimina un objeto RankingSystem del rankingList del torneo.
        
        Args:
            ranking_value (str): Valor del RankingSystem a eliminar
        """
        ranking_obj = RankingSystemClass.objects.get(value=ranking_value)
        self.rankingList.remove(ranking_obj)

    def cleanRankingList(self):
        """Limpia completamente el campo rankingList del torneo"""
        self.rankingList.clear()

    def getGames(self):
        """
        Devuelve todas las partidas del torneo, accediendo a través de las rondas.
        
        Returns:
            QuerySet: Todas las partidas del torneo.
        """
        from .game import Game 

        return Game.objects.filter(round__tournament=self)
    
    def __str__(self):
        """Devuelve el nombre del torneo"""
        return self.name        
    

class TournamentPlayers(models.Model):
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    registration_order = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Orden de registro"  
    )
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['registration_order']  
        

class RankingSystemClass(models.Model ) :
    value = models.CharField(
        max_length=2,
        choices=RankingSystem.choices,
        primary_key=True
        )
class TournamentRound(models.Model):
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)
    round = models.ForeignKey('Round', on_delete=models.CASCADE)
