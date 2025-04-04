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
    
    players = tournament.getPlayers()
    for player in players:
        results[player] = {PLAIN_SCORE: 0.0}
    
    
    games = Game.objects.filter(
        round__tournament=tournament,
        finished=True
    ).select_related('white', 'black')
    
    for game in games:
        if game.result == Scores.WHITE:
            results[game.white][PLAIN_SCORE] += tournament.win_points
            if game.black:
                results[game.black][PLAIN_SCORE] += tournament.lose_points 
        
        elif game.result == Scores.BLACK:
            if game.black:
                results[game.black][PLAIN_SCORE] += tournament.win_points 
            results[game.white][PLAIN_SCORE] += tournament.lose_points 
        
        elif game.result == Scores.DRAW:
            results[game.white][PLAIN_SCORE] += tournament.draw_points  
            if game.black:
                results[game.black][PLAIN_SCORE] += tournament.draw_points  
        
        # Casos de forfeit
        elif game.result == Scores.FORFEITWIN:
            results[game.white][PLAIN_SCORE] += tournament.win_points
            if game.black:
                results[game.black][PLAIN_SCORE] += tournament.lose_points 
        
        elif game.result == Scores.FORFEITLOSS:
            if game.black:
                results[game.black][PLAIN_SCORE] += tournament.win_points 
            results[game.white][PLAIN_SCORE] += tournament.lose_points 
        
        # Casos de bye
        elif game.result == Scores.BYE_H:
            results[game.white][PLAIN_SCORE] += tournament.draw_points  
        
        elif game.result == Scores.BYE_F:
            results[game.white][PLAIN_SCORE] += tournament.win_points  
        
        elif game.result == Scores.BYE_U:
            results[game.white][PLAIN_SCORE] += tournament.win_points 
        
        elif game.result == Scores.BYE_Z:
            pass  
        
       
        elif game.result == Scores.NOAVAILABLE:
            pass  
    
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