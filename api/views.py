from chess_models.models import create_rounds, Scores
from rest_framework import viewsets, permissions, pagination, status
from chess_models.models import Tournament, RankingSystemClass, Player, TournamentBoardType, Round, Referee, Game
from .serializers import TournamentSerializer, GameSerializer
from djoser.views import UserViewSet
from rest_framework.response import Response
from io import StringIO
import csv
import requests
from rest_framework.views import APIView
from chess_models.models import getRanking
from rest_framework.exceptions import PermissionDenied
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import MethodNotAllowed



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
    
class CustomUserViewSet(UserViewSet):   
    
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST', detail="Creating users is not allowed through this API.")
    


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def get_permissions(self):
        if self.action == 'update' or self.action == 'partial_update':
            return []
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.finished:
            if not request.user or not request.user.is_authenticated:
                raise PermissionDenied("You don't have permission to update this game.")

        response = super().update(request, *args, **kwargs)

        if not instance.finished:
            instance.refresh_from_db()
            instance.finished = True
            instance.save()

        return response


class RefereeViewSet(viewsets.ModelViewSet):
    queryset = Referee.objects.all()
    serializer_class = TournamentSerializer
    
class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.all()
    serializer_class = TournamentSerializer
    
class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = TournamentSerializer
    
class CreateRoundAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        tournament_id = int(request.data.get('tournament_id'))
        
        tournament = Tournament.objects.get(id=tournament_id)
            
        create_rounds(tournament, [])
            
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
        ).order_by('-name')
        
        serializer = TournamentSerializer(tournaments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TournamentCreateAPIView(APIView):
    permission_classes = []
    
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
        tournament = Tournament.objects.get(id=tournament_id)
    
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

class UpdateLichessGameAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        game_id = request.data.get('game_id')
        lichess_game_id = request.data.get('lichess_game_id')
        game = Game.objects.get(id=game_id)

        if game.finished:
            return Response(
                {"result": False, "message": "Game is blocked, only administrator can update it"},
                status=status.HTTP_403_FORBIDDEN
            )

        url = f"https://lichess.org/game/export/{lichess_game_id}"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response(
                {"result": False, "message": "Failed to fetch data for game"},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = response.json()

        lichess_white = data.get('players', {}).get('white', {}).get('user', {}).get('id')
        lichess_black = data.get('players', {}).get('black', {}).get('user', {}).get('id')

        expected_white = game.white.lichess_username
        expected_black = game.black.lichess_username

        if (lichess_white.lower() != expected_white.lower() or
            lichess_black.lower() != expected_black.lower()):
            return Response(
                {
                    "result": False,
                    "message": f"Players for game {lichess_game_id} are different: "
                                f"expected {expected_white} vs {expected_black}, got {lichess_white} vs {lichess_black}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        winner = data.get('winner', None)

        if winner == 'white':
            game.result = 'w'
        elif winner == 'black':
            game.result = 'b'
        else:
            game.result = '='

        game.finished = True
        game.save()

        return Response({"result": True, "message": "Game successfully updated"}, status=status.HTTP_200_OK)


        
class UpdateOTBGameAPIView(APIView):
    permission_classes = []
    
    def post(self, request):
        game_id = request.data.get('game_id')
        otb_result = request.data.get('otb_result')
        email = request.data.get('email')
        
        game = Game.objects.get(id=game_id)
            
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
        game = Game.objects.get(id=game_id)
            
        if game.round.tournament.administrativeUser != request.user:
            return Response(
                {"result": False, "message": "Only the user that create the tournament can update it"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        game.result = otb_result
        game.finished = True
        game.save()
        
        return Response(
            {"result": True, "message": "Game updated by administrator"},
            status=status.HTTP_200_OK
        )