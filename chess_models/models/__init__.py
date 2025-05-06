# chess_models/models/__init__.py
from .player import Player, LichessAPIError
from .referee import Referee
from .tournament import Tournament, RankingSystemClass, TournamentRound
from .round import Round
from .game import Game, create_rounds


from chess_models.constants import (
    TournamentType, 
    TournamentSpeed, 
    TournamentBoardType, 
    RankingSystem,
    Scores,
    Color,
    LICHESS_USERS
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
            if game.black in results:
                results[game.black][PLAIN_SCORE] += tournament.lose_points
        
        elif game.result == Scores.BLACK:
            if game.black in results:
                results[game.black][PLAIN_SCORE] += tournament.win_points
            results[game.white][PLAIN_SCORE] += tournament.lose_points
        
        elif game.result == Scores.DRAW:
            results[game.white][PLAIN_SCORE] += tournament.draw_points
            if game.black in results:
                results[game.black][PLAIN_SCORE] += tournament.draw_points
        
        elif game.result == Scores.FORFEITWIN:
            results[game.white][PLAIN_SCORE] += tournament.win_points
        
        elif game.result == Scores.FORFEITLOSS:
            if game.black in results:
                results[game.black][PLAIN_SCORE] += tournament.win_points
        
        elif game.result == Scores.BYE_H:
            results[game.white][PLAIN_SCORE] += tournament.draw_points
        
        elif game.result == Scores.BYE_F:
            results[game.white][PLAIN_SCORE] += tournament.win_points
        
        elif game.result == Scores.BYE_U:
            results[game.white][PLAIN_SCORE] += tournament.win_points
            
    return results

def getBlackWins(tournament, results):
    WINS = RankingSystem.WINS.value
    BLACKTIMES = RankingSystem.BLACKTIMES.value
    
    for player in results:
        results[player][WINS] = 0
        results[player][BLACKTIMES] = 0
    
    played_games = Game.objects.filter(
        round__tournament=tournament,
        finished=True,
        result__in=[Scores.WHITE, Scores.BLACK, Scores.DRAW]
    ).select_related('white', 'black')
    
    for game in played_games:
        if game.result == Scores.WHITE:
            results[game.white][WINS] += 1
        elif game.result == Scores.BLACK:
            results[game.black][WINS] += 1
        
        results[game.black][BLACKTIMES] += 1
    
    return results
def getRanking(tournament):
    player_scores = getScores(tournament)
    player_scores = getBlackWins(tournament, player_scores)

    plain_score_field = RankingSystem.PLAIN_SCORE.value
    ranking_criteria = [criterion.value for criterion in tournament.rankingList.all()]

    players = tournament.getPlayers(sorted=True)
    ranking_list = []

    for player in players:
        player_data = {
            "player": player,
            "plain_score": player_scores[player][plain_score_field],
        }

        for criterion in ranking_criteria:
            player_data[criterion] = player_scores[player].get(criterion, 0)

        ranking_list.append(player_data)

    rounds_completed = False
    for round in tournament.round_set.all():
        if round.game_set.filter(finished=True).exists():
            rounds_completed = True
            break

    def sort_by_ranking(entry):
        values = [-entry.get("plain_score", 0)]
        for criterion in ranking_criteria:
            value = entry.get(criterion, 0)   
            if isinstance(value, (int, float)):
                values.append(-value)
            else:
                values.append(value) 
        return tuple(values)

    ranking_list.sort(key=sort_by_ranking)

    ranked_players = {}
    rank_counter = 1
    for data in ranking_list:
        player = data["player"]
        player_stats = {
            "rank": rank_counter,
            plain_score_field: data["plain_score"]
        }

        for criterion in ranking_criteria:
            player_stats[criterion] = data[criterion]

        ranked_players[player] = player_stats
        rank_counter += 1

    return ranked_players




