# chess_models/models/__init__.py
# Primero importa los modelos básicos
from .player import Player, LichessAPIError
from .referee import Referee
from .tournament import Tournament, RankingSystemClass, TournamentRound
from .round import Round
from .game import Game, create_rounds  # Asegúrate de importar create_rounds desde game

# Luego importa las constantes
from chess_models.constants import (
    TournamentType, 
    TournamentSpeed, 
    TournamentBoardType, 
    RankingSystem,
    Scores,
    Color
)

def getScores(tournament):
    
    PLAIN_SCORE = RankingSystem.PLAIN_SCORE.value
    results = {}
    
    # Inicializar puntuaciones para todos los jugadores
    players = tournament.getPlayers()
    for player in players:
        results[player] = {PLAIN_SCORE: 0.0}
    
    # Obtener todos los juegos terminados del torneo
    games = Game.objects.filter(
        round__tournament=tournament,
        finished=True
    ).select_related('white', 'black')
    
    # Calcular puntuaciones según reglas específicas del test
    for game in games:
        if game.result == Scores.WHITE:
            results[game.white][PLAIN_SCORE] += 1.0  # Victoria blanca = 1 punto
            if game.black:
                results[game.black][PLAIN_SCORE] += 0.0  # Derrota negra = 0 puntos
        elif game.result == Scores.BLACK:
            if game.black:
                results[game.black][PLAIN_SCORE] += 1.0  # Victoria negra = 1 punto
            results[game.white][PLAIN_SCORE] += 0.0  # Derrota blanca = 0 puntos
        elif game.result == Scores.DRAW:
            results[game.white][PLAIN_SCORE] += 0.5  # Empate = 0.5 puntos
            if game.black:
                results[game.black][PLAIN_SCORE] += 0.5  # Empate = 0.5 puntos
    
    return results

def getBlackWins(tournament, results):
    
    WINS = RankingSystem.WINS.value
    BLACKTIMES = RankingSystem.BLACKTIMES.value
    
    # Inicializar contadores
    players = tournament.getPlayers()
    for player in players:
        results[player][WINS] = 0
        results[player][BLACKTIMES] = 0
    
    # Obtener todos los juegos terminados
    games = Game.objects.filter(
        round__tournament=tournament,
        finished=True
    ).select_related('white', 'black')
    
    # Contar victorias y veces con negras
    for game in games:
        if game.result == Scores.WHITE:
            results[game.white][WINS] += 1
        elif game.result == Scores.BLACK and game.black:
            results[game.black][WINS] += 1
        
        # Contar solo si el jugador con negras existe y no es un BYE
        if game.black and str(game.black) != 'BYE1':
            results[game.black][BLACKTIMES] += 1
    
    return results

def getRanking(tournament):
    
    # Obtener puntuaciones básicas
    results = getScores(tournament)
    
    # Añadir estadísticas de victorias y veces con negras
    results = getBlackWins(tournament, results)
    
    # Ordenar jugadores según criterios del torneo
    ranking_systems = [rs.value for rs in tournament.rankingList.all()]
    if not ranking_systems:
        ranking_systems = [RankingSystem.PLAIN_SCORE.value]
    
    players = list(results.keys())
    
    def sort_key(player):
        key = []
        for system in ranking_systems:
            if system == RankingSystem.PLAIN_SCORE.value:
                key.append(-results[player].get(system, 0))  # Orden descendente
            elif system == RankingSystem.WINS.value:
                key.append(-results[player].get(system, 0))  # Orden descendente
            elif system == RankingSystem.BLACKTIMES.value:
                key.append(results[player].get(system, 0))   # Orden ascendente
            else:
                key.append(0)
        return tuple(key)
    
    players.sort(key=sort_key)
    
    # Asignar posiciones finales
    for i, player in enumerate(players, 1):
        results[player]['rank'] = i
    
    return results