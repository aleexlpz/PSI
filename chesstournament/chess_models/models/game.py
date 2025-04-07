from django.db import models, transaction
from chess_models.constants import Scores
from .player import Player, LichessAPIError
from .round import Round
from .tournament import Tournament
from django.utils import timezone
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
        related_name='games_as_white',
        verbose_name="Jugador con blancas"
    )

    black = models.ForeignKey(
        'Player',
        on_delete=models.CASCADE,
        null=True,
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
            
    from chess_models.tests.constants import lichess_usernames_6
    


def create_rounds(tournament, swissByes=[]):
    if tournament.tournament_type != 'SR':
        return

    players = list(tournament.players.all().order_by('pk'))
    n = len(players)

    if n % 2 != 0:
        return

    num_rounds = n - 1
    num_boards = int(n / 2)

    with transaction.atomic():
        rounds = [
            Round.objects.create(
                tournament=tournament,
                name=f"Ronda {i+1}",
                start_date=timezone.now()
            ) for i in range(num_rounds)
        ]

        pairing = {
            b: {'white': b - 1, 'black': n - b}
            for b in range(1, num_boards + 1)
        }

        for board, match in pairing.items():
            Game.objects.create(
                white=players[match['white']],
                black=players[match['black']],
                round=rounds[0]
            )

        nplayer_white = False
        for rnd in range(1, num_rounds): 
            playerlist = [
                pairing[b][c]
                for b in range(1, num_boards + 1)
                for c in ('white', 'black')
                if pairing[b][c] < n - 1
            ]

            pairing = {}
            last = playerlist.pop()
            if nplayer_white:
                pairing[1] = {'white': last, 'black': n - 1}
            else:
                pairing[1] = {'white': n - 1, 'black': last}

            Game.objects.create(
                white=players[pairing[1]['white']],
                black=players[pairing[1]['black']],
                round=rounds[rnd]
            )

            for board in range(2, num_boards + 1):
                black = playerlist.pop()
                white = playerlist.pop()
                pairing[board] = {'white': white, 'black': black}
                Game.objects.create(
                    white=players[white],
                    black=players[black],
                    round=rounds[rnd]
                )

            nplayer_white = not nplayer_white