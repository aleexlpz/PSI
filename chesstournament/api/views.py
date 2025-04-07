from chess_models.models import create_rounds, Scores
from rest_framework import viewsets, permissions, pagination, status
from chess_models.models import Tournament, RankingSystemClass, Player, TournamentBoardType, Round, Referee, Game
from .serializers import TournamentSerializer, GameSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.response import Response
from io import StringIO
import csv
import requests
from rest_framework.views import APIView
from chess_models.models import getRanking


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class TournamentViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    queryset = Tournament.objects.all().order_by('-start_date', '-id')
    serializer_class = TournamentSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = []
        return super().get_permissions()
    
class CustomUserViewSet(DjoserUserViewSet):
    def create(self, request, *args, **kwargs):
        return Response(
            {"result": False, "message": "User creation is not allowed via API"},
            status=status.HTTP_403_FORBIDDEN
        )
    
class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    
    def get_permissions(self):
        if self.action == 'update' and self.get_object().finished == True:
            self.permission_classes = permissions.IsAuthenticated
        return super().get_permissions()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_staff:
            print("SOY STAFF")
            super().update(request, *args, **kwargs) 
            return Response(
                status=status.HTTP_200_OK,
            )
        elif not request.user.is_staff and instance.finished == True:
            print("NOS SOY STAFF Y LA PARTIDA ESTA TERMINADA")
            super().update(request, *args, **kwargs)
            return Response(
                {"result": False, "message": "Game is blocked, only administrator can update it"},
                status=status.HTTP_403_FORBIDDEN
            )
        elif not request.user.is_staff and instance.finished == False:
            print("NO SOY STAFF Y LA PARTIDA NO ESTA TERMINADA")
            super().update(request, *args, **kwargs)
            return Response(
                {"result": True, "message": "Game updated"},
                status=status.HTTP_200_OK,
            )
        else:
            print("NO SOY NADA")
            super().update(request, *args, **kwargs)
            return Response(
                {"result": False, "message": "Game is blocked, only administrator can update it"},
                status=status.HTTP_403_FORBIDDEN
            )

class RefereeViewSet(viewsets.ModelViewSet):
    queryset = Referee.objects.all()
    serializer_class = TournamentSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.all()
    serializer_class = TournamentSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = TournamentSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
class CreateRoundAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        tournament_id = int(request.data.get('tournament_id'))
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response(
                {"result": False, "message": "Tournament does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if tournament.getPlayersCount() == 0:
            return Response(
                {"result": False, "message": "Tournament has no players"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        create_rounds(tournament, [])
        
        if tournament.round_set.count() == 0:
            return Response(
                {"result": False, "message": "Failed to create rounds"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response(
            {"result": True, "message": "Rounds created successfully"},
            status=status.HTTP_201_CREATED
        )
    
class SearchTournamentsAPIView(APIView):
    permission_classes = []
    
    def post(self, request):
        search_string = request.data.get('search_string')
        if not search_string:
            return Response(
                {"result": False, "message": "search_string is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        tournaments = Tournament.objects.filter(
            name__icontains=search_string
        ).order_by('-start_date')
        
        serializer = TournamentSerializer(tournaments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TournamentCreateAPIView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        print("DATOS INICIO" + str(request.data))
        # Validar datos básicos
        name = request.data.get('name')
        if not name:
            return Response(
                {"result": False, "message": "Name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if Tournament.objects.filter(name=name).exists():
            return Response(
                {"result": False, "message": "Tournament with this name already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        print("CREAR TORNEO")
        # Crear torneo
        tournament = Tournament(
            name=name,
            administrativeUser=request.user,
            only_administrative=request.data.get('only_administrative', False),
            tournament_type=request.data.get('tournament_type'),
            board_type=request.data.get('board_type'),
            win_points=float(request.data.get('win_points', 1.0)),
            draw_points=float(request.data.get('draw_points', 0.5)),
            lose_points=float(request.data.get('lose_points', 0.0)),
            tournament_speed=request.data.get('tournament_speed'),
            timeControl=request.data.get('timeControl', '15+0'),
        )
        tournament.save()
        
        # Añadir rankingList
        ranking_list = request.data.get('rankingList', [])
        for rank_system in ranking_list:
            try:
                system = RankingSystemClass.objects.get(value=rank_system)
                tournament.rankingList.add(system)
            except RankingSystemClass.DoesNotExist:
                pass
                
        # Añadir jugadores
        players_csv = request.data.get('players', '')
        if players_csv:
            buffer = StringIO(players_csv)
            reader = csv.DictReader(buffer)
            
            for row in reader:
                if tournament.board_type == TournamentBoardType.LICHESS:
                    lichess_username = row.get('lichess_username')
                    if lichess_username:
                        player, _ = Player.objects.get_or_create(
                            lichess_username=lichess_username
                        )
                        tournament.players.add(player)
                else:
                    name = row.get('name')
                    email = row.get('email')
                    if name and email:
                        player, _ = Player.objects.get_or_create(
                            name=name, email=email
                        )
                        tournament.players.add(player)
        
        serializer = TournamentSerializer(tournament)
        print("DATOS" + serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class GetRanking(APIView):
    permission_classes = []
    
    def get(self, request, tournament_id):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response(
                {"result": False, "message": "Tournament does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        ranking = getRanking(tournament)
        response_data = {}
        
        for player, data in ranking.items():
            player_data = {
                'id': player.id,
                'name': player.lichess_username if player.lichess_username else player.name,
                'score': data.get('PS', 0),
                'rank': data.get('rank', 0),
            }
            
            if 'WI' in data:
                player_data['WI'] = data['WI']
            if 'BT' in data:
                player_data['BT'] = data['BT']
                
            response_data[str(player.id)] = player_data
            
        return Response(response_data, status=status.HTTP_200_OK)

class GetPlayers(APIView):
    permission_classes = []
    
    def get(self, request, tournament_id):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response(
                {"result": False, "message": "Tournament does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        players = tournament.getPlayers()
        response_data = []
        
        for player in players:
            player_data = {
                'id': player.id,
                'name': player.name,
                'email': player.email,
                'country': player.country,
                'lichess_username': player.lichess_username,
                'fide_id': player.fide_id,
                'ratings': {
                    'bullet': player.lichess_rating_bullet,
                    'blitz': player.lichess_rating_blitz,
                    'rapid': player.lichess_rating_rapid,
                    'classical': player.lichess_rating_classical,
                    'fide_blitz': player.fide_rating_blitz,
                    'fide_rapid': player.fide_rating_rapid,
                    'fide_classical': player.fide_rating_classical,
                }
            }
            response_data.append(player_data)
            
        return Response(response_data, status=status.HTTP_200_OK)
    
class GetRoundResults(APIView):
    permission_classes = []
    
    def get(self, request, tournament_id):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response(
                {"result": False, "message": "Tournament does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        rounds = tournament.round_set.all().order_by('id')
        games = Game.objects.filter(round__tournament=tournament).order_by('-rankingOrder')
        ranking = getRanking(tournament)
        
        results = {}
        for round_obj in rounds:
            round_games = games.filter(round=round_obj)
            round_data = {
                'round_id': round_obj.id,
                'round_name': round_obj.name,
                'start_date': round_obj.start_date,
                'games': []
            }
            
            for game in round_games:
                game_data = {
                    'id': game.id,
                    'rankingOrder': game.rankingOrder,
                    'white': {
                        'id': game.white.id if game.white else None,
                        'name': game.white.lichess_username if game.white and game.white.lichess_username else game.white.name if game.white else None
                    },
                    'black': {
                        'id': game.black.id if game.black else None,
                        'name': game.black.lichess_username if game.black and game.black.lichess_username else game.black.name if game.black else None
                    },
                    'result': game.result
                }
                round_data['games'].append(game_data)
                
            results[str(round_obj.id)] = round_data
            
        return Response(results, status=status.HTTP_200_OK)
    
class UpdateLichessGameAPIView(APIView):
    permission_classes = []
    authentication_classes = []
    
    def post(self, request):
        game_id = request.data.get('game_id')
        lichess_game_id = request.data.get('lichess_game_id')
        
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"result": False, "message": "Game does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if game.finished:
            return Response(
                {"result": False, "message": "Game is blocked, only administrator can update it"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        try:
            url = f"https://lichess.org/api/game/{lichess_game_id}"
            response = requests.get(url)
            if response.status_code != 200:
                return Response(
                    {"result": False, "message": "Failed to fetch data for game"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            data = response.json()
            winner = data.get('winner')
            
            if winner == 'white':
                game.result = 'w'
            elif winner == 'black':
                game.result = 'b'
            else:
                game.result = '='
                
            game.finished = True
            game.save()
            
            return Response({"result": True}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"result": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class UpdateOTBGameAPIView(APIView):
    permission_classes = []
    
    def post(self, request):
        game_id = request.data.get('game_id')
        otb_result = request.data.get('otb_result')
        email = request.data.get('email')
        
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"result": False, "message": "Game does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if game.finished:
            return Response(
                {"result": False, "message": "Game is blocked, only administrator can update it"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        if not ((game.white and game.white.email == email) or 
                (game.black and game.black.email == email)):
            return Response(
                {"result": False, "message": "Email does not match any player in this game"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        if otb_result not in ['w', 'b', '=']:
            return Response(
                {"result": False, "message": "Invalid result. Must be 'w', 'b' or '='"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        game.result = otb_result
        game.finished = True
        game.save()
        
        return Response(
            {"result": True, "message": "Game updated by player"},
            status=status.HTTP_200_OK
        )
    
class AdminUpdateGameAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        game_id = request.data.get('game_id')
        otb_result = request.data.get('otb_result')
        
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"result": False, "message": "Game does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if game.round.tournament.administrativeUser != request.user:
            return Response(
                {"result": False, "message": "Only the user that create the tournament can update it"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        if otb_result not in ['w', 'b', '=']:
            return Response(
                {"result": False, "message": "Invalid result. Must be 'w', 'b' or '='"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        game.result = otb_result
        game.finished = True
        game.save()
        
        return Response(
            {"result": True, "message": "Game updated by administrator"},
            status=status.HTTP_200_OK
        )