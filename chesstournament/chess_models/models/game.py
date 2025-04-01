from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from chess_models.constants import Scores
import requests

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
        """
        Obtiene el resultado de una partida desde Lichess.org
        Devuelve: (resultado, jugador blanco, jugador negro)
        """
        
        try:
            url = f"https://lichess.org/api/game/{lichess_game_id}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                winner = data.get('winner')
                white_user = data.get('players', {}).get('white', {}).get('user', {}).get('name')
                black_user = data.get('players', {}).get('black', {}).get('user', {}).get('name')
                
                # Mapear resultado a nuestros códigos
                if winner == 'white':
                    return Scores.WHITE, white_user, black_user
                elif winner == 'black':
                    return Scores.BLACK, white_user, black_user
                else:
                    return Scores.DRAW, white_user, black_user
            else:
                raise ConnectionError("No se pudo obtener la partida de Lichess")
        except requests.RequestException as e:
            raise ConnectionError(f"Error de conexión con Lichess: {str(e)}")
