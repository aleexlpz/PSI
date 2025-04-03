from django.test import TransactionTestCase, tag
from chess_models.models import Player, Referee, Tournament, Game, Round
from chess_models.models import (TournamentSpeed,
                                 TournamentType, TournamentBoardType,
                                 RankingSystem, getRanking, RankingSystemClass)
from chess_models.models import Scores
from chess_models.tests.constants import (
    lichess_usernames_6, lichess_usernames_8)


class TournamentModelTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        pass
        # reset_sequences()

    @tag("continua")
    def test_001_tournament_str_method(self):
        "create a tournament "
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name)
        self.assertEqual(str(tournament), tournament_name)

    @tag("continua")
    def test_002_tournament_add_players(self):
        """add players to tournament,
           check tournament.players is a manytomany field
        """
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name)
        players = []  # used for testing
        for lichess_username in lichess_usernames_6:
            player = Player.objects.create(
                lichess_username=lichess_username)
            tournament.players.add(player)
            players.append(player)
        for player in players:
            self.assertTrue(player in tournament.getPlayers())
        self.assertEqual(tournament.getPlayersCount(),
                         len(lichess_usernames_6))

    @tag("continua")
    def test_003_tournament_add_referee(self):
        "add referee to tournament"
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name)
        referee = Referee.objects.create(
            name='referee_01', refereeNumber='12345678')
        tournament.referee = referee
        self.assertEqual(tournament.referee, referee)

    @tag("continua")
    def test_0030_RankingSystemClass(self):
        "create a RankingSystemClass"
        rankingSystem = RankingSystem.BUCHHOLZ
        rankingSystemClass = RankingSystemClass.objects.create(
            value=rankingSystem)
        self.assertEqual(rankingSystemClass.value, rankingSystem)

    @tag("continua")
    def test_0035_tournament_rankingList(self):
        """add rankingList to tournament
        Ranking are saved as manytomany field in the model Tournament
        """
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name)
        rankingSystem1 = RankingSystem.BUCHHOLZ
        rankingSystem2 = RankingSystem.SONNEBORN_BERGER
        tournament.addToRankingList(rankingSystem1)
        tournament.addToRankingList(rankingSystem2)
        rankingSystemList = [r.value for r in tournament.getRankingList()]
        self.assertEqual(tournament.rankingList.count(), 2)
        self.assertTrue(rankingSystem1 in rankingSystemList)
        self.assertTrue(rankingSystem2 in rankingSystemList)

    @tag("continua")
    def test_004_tournament_number_of_players(self):
        "check function getPlayersCount,  number of "
        "players in tournament"
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name)
        players = []
        for lichess_username in lichess_usernames_6:
            player = Player.objects.create(
                lichess_username=lichess_username)
            tournament.players.add(player)
            players.append(player)
        self.assertEqual(tournament.getPlayersCount(),
                         len(lichess_usernames_6))

    # ROB: getPlayers: needed
    @tag("suiza")
    def test_005_getSortedPlayers(self):
        """check function getSortedPlayers that
        returns a sorted  list of players. The sorted is done by
        rating. The choosed rating depends on the TournamentSpeed
        and board_type. First player is the one with the highest
        rating"""
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name,
            board_type=TournamentBoardType.LICHESS,
            tournament_type=TournamentType.ROUNDROBIN,
            tournament_speed=TournamentSpeed.RAPID)
        for lichess_username in lichess_usernames_6:
            player = Player.objects.create(
                lichess_username=lichess_username)
            tournament.players.add(player)
        sorted_players = tournament.getPlayers(sorted=True)

        ranting = 9999999
        for player in sorted_players:
            self.assertTrue(ranting >= player.lichess_rating_rapid)
            ranting = player.lichess_rating_rapid

    