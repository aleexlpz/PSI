# chess_models/models/__init__.py
from chess_models.constants import TournamentType, TournamentSpeed, Scores, TournamentBoardType, RankingSystem, Color
from chess_models.models.player import Player, LichessAPIError
from chess_models.models.tournament import Tournament, TournamentPlayers, RankingSystemClass
from chess_models.models.round import Round
from chess_models.models.game import Game
from chess_models.models.referee import Referee
from django.db.models import Q

def getScores(tournament):
    """
    Devuelve un diccionario con las puntuaciones de los jugadores en el torneo.
    Clave: jugador, Valor: diccionario con al menos {'PS': puntuación}
    """
    PLAIN_SCORE = RankingSystem.PLAIN_SCORE.value
    results = {}
    
    # Inicializar puntuaciones
    players = tournament.getPlayers()
    for player in players:
        results[player] = {PLAIN_SCORE: 0.0}
    
    # Calcular puntuaciones basadas en partidas terminadas
    games = tournament.game_set.filter(finished=True)
    for game in games:
        if game.result == Scores.WHITE:
            results[game.white][PLAIN_SCORE] += tournament.win_points
            results[game.black][PLAIN_SCORE] += tournament.lose_points
        elif game.result == Scores.BLACK:
            results[game.black][PLAIN_SCORE] += tournament.win_points
            results[game.white][PLAIN_SCORE] += tournament.lose_points
        elif game.result == Scores.DRAW:
            results[game.white][PLAIN_SCORE] += tournament.draw_points
            results[game.black][PLAIN_SCORE] += tournament.draw_points
    
    return results

def getBlackWins(tournament, results):
    """
    Añade información sobre victorias y veces jugando con negras al diccionario results.
    Modifica el diccionario results in-place.
    """
    WINS = RankingSystem.WINS.value
    BLACKTIMES = RankingSystem.BLACKTIMES.value
    
    # Inicializar contadores
    for player in results:
        results[player][WINS] = 0
        results[player][BLACKTIMES] = 0
    
    # Contar victorias y veces con negras
    games = tournament.game_set.filter(finished=True)
    for game in games:
        if game.black:
            results[game.black][BLACKTIMES] += 1
            
            if game.result == Scores.BLACK:
                results[game.black][WINS] += 1
        
        if game.white and game.result == Scores.WHITE:
            results[game.white][WINS] += 1
    
    return results

def getRanking(tournament):
    """
    Devuelve un diccionario con el ranking de jugadores ordenado según:
    1. Puntuación (PS)
    2. Criterios de desempate en rankingList
    """
    # Obtener puntuaciones básicas
    results = getScores(tournament)
    
    # Añadir información de victorias y veces con negras
    results = getBlackWins(tournament, results)
    
    # Si no hay partidas jugadas, devolver jugadores en orden de inscripción
    if tournament.get_number_of_rounds_with_games() == 0:
        players = tournament.getPlayers()
        for i, player in enumerate(players, 1):
            results[player]['rank'] = i
        return results
    
    # Ordenar jugadores según criterios
    players = list(results.keys())
    ranking_criteria = [rs.value for rs in tournament.rankingList.all()]
    
    # Función para obtener clave de ordenación
    def get_sort_key(player):
        key = [-results[player][RankingSystem.PLAIN_SCORE.value]]  # Orden descendente por puntuación
        
        for criterion in ranking_criteria:
            if criterion in results[player]:
                # Orden descendente para WINS, ascendente para BLACKTIMES
                multiplier = -1 if criterion == RankingSystem.WINS.value else 1
                key.append(multiplier * results[player][criterion])
        
        return tuple(key)
    
    # Ordenar jugadores
    players_sorted = sorted(players, key=get_sort_key)
    
    # Asignar posiciones en el ranking
    for rank, player in enumerate(players_sorted, 1):
        results[player]['rank'] = rank
    
    return results