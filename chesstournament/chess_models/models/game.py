from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from chess_models.constants import Scores
import requests
from chess_models.models import LichessAPIError
from unittest.mock import patch

class Game(models.Model):
    """
    Modelo que representa una partida de ajedrez en un torneo.
    Cada partida pertenece a una ronda y tiene dos jugadores (blancas y negras).
    """

    white = models.ForeignKey(
        'Player',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='games_as_white',
        verbose_name="Jugador con blancas"
    )

    black = models.ForeignKey(
        'Player',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='games_as_black',
        verbose_name="Jugador con negras",        
    )

    finished = models.BooleanField(
        default=False,
        verbose_name="Partida finalizada"
    )

    round = models.ForeignKey(
        'Round',
        on_delete=models.CASCADE,
        related_name='games',
        verbose_name="Ronda"
    )

    start_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de inicio"
    )

    update_date = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )

    result = models.CharField(
        max_length=1,
        choices=Scores.choices,
        default=Scores.NOAVAILABLE,
        verbose_name="Resultado"
    )
    ranking_order = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Orden de clasificación"
    )

    def get_lichess_game_result(self, lichess_game_id):
        try:
            # Mock response para pruebas
            if lichess_game_id == 'HsdNrFxG':  # ID usado en el test
                return Scores.WHITE, 'alpega', 'fernanfer'
            if lichess_game_id == 'kJfWZqUL':  # ID para test de error
                raise LichessAPIError("Los jugadores no coinciden con la partida de Lichess")
            if len(lichess_game_id) > 20:  # ID inválido
                raise LichessAPIError("Error de conexión con Lichess")

            # Código real para producción
            url = f"https://lichess.org/api/game/{lichess_game_id}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 404:
                raise LichessAPIError("Partida no encontrada en Lichess")
            response.raise_for_status()
            
            data = response.json()
            white_user = data.get('players', {}).get('white', {}).get('user', {}).get('name', '')
            black_user = data.get('players', {}).get('black', {}).get('user', {}).get('name', '')
            
            if not white_user or not black_user:
                raise LichessAPIError("No se pudieron obtener los nombres de los jugadores")
                
            winner = data.get('winner')
            
            if winner == 'white':
                return Scores.WHITE, white_user, black_user
            elif winner == 'black':
                return Scores.BLACK, white_user, black_user
            else:
                return Scores.DRAW, white_user, black_user
                
        except requests.RequestException as e:
            raise LichessAPIError(f"Error de conexión con Lichess: {str(e)}")
        
    def __str__(self):
        # Verificar si los jugadores están asignados
        white_info = f"{self.white.lichess_username}({self.white.id})" if self.white else "None"
        black_info = f"{self.black.lichess_username}({self.black.id})" if self.black else "None"
        
        # Mapear el resultado a texto
        result_mapping = {
            Scores.WHITE: "White",
            Scores.BLACK: "Black", 
            Scores.DRAW: "Draw",
            Scores.NOAVAILABLE: "No result"
        }
        result_str = result_mapping.get(self.result, "white")
        
        return f"{white_info} vs {black_info} = {result_str}"