from django.shortcuts import render
from rest_framework import viewsets
from chess_models.models import Referee, Player, Game, Tournament, Round
from django.contrib.auth.models import User
from .serializers import (
    RefereeSerializer,
    PlayerSerializer,
    GameSerializer,
    TournamentSerializer,
    RoundSerializer,
    CustomUserSerializer
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import TournamentSerializer
from django.shortcuts import get_object_or_404
import csv
from io import StringIO
from chess_models.models.game import create_rounds
from chess_models.models import getRanking



class RefereeViewSet(viewsets.ModelViewSet):
    queryset = Referee.objects.all()
    serializer_class = RefereeSerializer

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]  # Por defecto requiere autenticación

    def get_permissions(self):
        # Permite actualizar sin autenticación si el juego no ha terminado
        if self.action == 'update' and self.get_object().finished is False:
            self.permission_classes = []
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Solo permite actualizar si el juego no ha terminado
        if instance.finished:
            return Response(
                {"detail": "Cannot update a finished game."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response = super().update(request, *args, **kwargs)
        
        # Marca el juego como terminado después de actualizar
        if response.status_code == status.HTTP_200_OK:
            instance.finished = True
            instance.save()
        
        return response

class CustomPagination(PageNumberPagination):
    """Paginación personalizada para torneos"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class TournamentViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    queryset = Tournament.objects.all().order_by('-start_date', '-id')
    serializer_class = TournamentSerializer
    permission_classes = [IsAuthenticated]  # Por defecto requiere autenticación

    def get_permissions(self):
        # No requiere autenticación para listar o ver detalles
        if self.action in ['list', 'retrieve']:
            self.permission_classes = []
        return super().get_permissions()

class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer

class CustomUserViewSet(UserViewSet):
    def create(self, request, *args, **kwargs):
        # Bloquea la creación de usuarios a través de este endpoint
        return Response(
            {"detail": "User creation is not allowed via this endpoint."},
            status=status.HTTP_403_FORBIDDEN
        )

# Endpoint para crear rondas
class CreateRoundAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        tournament_id = int(request.data.get('tournament_id'))
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response(
                {"result": False, "message": "Tournament not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if tournament.players.count() == 0:
            return Response(
                {"result": False, "message": "No players in tournament"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Lógica para crear rondas (implementar según tu sistema)
        try:
            create_rounds(tournament, [])
            return Response(
                {"result": True},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"result": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

# Endpoint para buscar torneos
class SearchTournamentsAPIView(APIView):
    permission_classes = []

    def post(self, request):
        search_string = request.data.get('search_string')
        if not search_string:
            return Response({
                "result": False,
                "message": "search_string is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        tournaments = Tournament.objects.filter(name__icontains=search_string)
        serializer = TournamentSerializer(tournaments, many=True)
        return Response({
            "result": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

# Endpoint para crear torneos
class TournamentCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Validar que no exista torneo con mismo nombre
        if Tournament.objects.filter(name=request.data.get('name')).exists():
            return Response({
                "result": False,
                "message": "Tournament with this name already exists"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Procesar jugadores
        players_data = request.data.get('players', '')
        players = []
        try:
            if request.data.get('board_type') == 'OTB':
                reader = csv.DictReader(StringIO(players_data), fieldnames=['name', 'email'])
                for row in reader:
                    players.append({'name': row['name'], 'email': row['email']})
            else:  # LICHESS
                reader = csv.reader(StringIO(players_data))
                for row in reader:
                    if row:  # Skip empty lines
                        players.append({'lichess_username': row[0]})
        except Exception as e:
            return Response({
                "result": False,
                "message": f"Error processing players: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Crear torneo
        try:
            tournament = Tournament.objects.create(
                name=request.data.get('name'),
                tournament_type=request.data.get('tournament_type'),
                board_type=request.data.get('board_type'),
                administrative_user=request.user,
                # ... otros campos del torneo
            )
            
            # Añadir jugadores (implementar según tu modelo)
            self._add_players_to_tournament(tournament, players)
            
            serializer = TournamentSerializer(tournament)
            return Response({
                "result": True,
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "result": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def _add_players_to_tournament(self, tournament, players):
        # Implementar lógica para añadir jugadores al torneo
        pass

# Endpoint para obtener ranking
class GetRanking(APIView):
    permission_classes = []

    def get(self, request, tournament_id):
        tournament = get_object_or_404(Tournament, id=tournament_id)
        
        ranking = getRanking(tournament)  # Implementar esta función
        return Response({
            "result": True,
            "data": ranking
        }, status=status.HTTP_200_OK)

class GetPlayers(APIView):
    permission_classes = []

    def get(self, request, tournament_id):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({
                "result": False,
                "message": "Tournament not found"
            }, status=status.HTTP_404_NOT_FOUND)

        players = tournament.players.all()  # Asume que tienes una relación players en Tournament
        player_data = []
        
        for player in players:
            player_data.append({
                'id': player.id,
                'name': player.name,
                'email': player.email if hasattr(player, 'email') else None,
                'lichess_username': player.lichess_username if hasattr(player, 'lichess_username') else None
            })

        return Response({
            "result": True,
            "data": player_data
        }, status=status.HTTP_200_OK)

# Endpoint para resultados de rondas
class GetRoundResults(APIView):
    permission_classes = []

    def get(self, request, tournament_id):
        tournament = get_object_or_404(Tournament, id=tournament_id)
        
        rounds = Round.objects.filter(tournament=tournament).order_by('id')
        results = []
        
        for round in rounds:
            round_data = {
                'round_id': round.id,
                'round_name': round.name,
                'start_date': round.start_date,
                'games': []
            }
            
            games = Game.objects.filter(round=round).order_by('-white__ranking')
            for game in games:
                game_data = {
                    'id': game.id,
                    'rankingOrder': game.white.ranking,
                    'white': {
                        'id': game.white.id,
                        'name': game.white.name
                    },
                    'black': {
                        'id': game.black.id if game.black else None,
                        'name': game.black.name if game.black else None
                    },
                    'result': game.result
                }
                round_data['games'].append(game_data)
            
            results.append(round_data)
        
        return Response({
            "result": True,
            "data": results
        }, status=status.HTTP_200_OK)

# Endpoint para actualizar juegos de Lichess
class UpdateLichessGameAPIView(APIView):
    permission_classes = []

    def post(self, request):
        game_id = request.data.get('game_id')
        lichess_game_id = request.data.get('lichess_game_id')
        
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response({
                "result": False,
                "message": "Game does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if game.finished:
            return Response({
                "result": False,
                "message": "Game is finished, only admin can update"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Implementar lógica para obtener resultado de Lichess
            winner = game.get_lichess_game_result(lichess_game_id)
            game.result = winner
            game.finished = True
            game.save()
            
            return Response({
                "result": True
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "result": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

# Endpoint para actualizar juegos OTB
class UpdateOTBGameAPIView(APIView):
    permission_classes = []

    def post(self, request):
        game_id = request.data.get('game_id')
        otb_result = request.data.get('otb_result')
        email = request.data.get('email')
        
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response({
                "result": False,
                "message": "Game does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if game.finished:
            return Response({
                "result": False,
                "message": "Game is finished, only admin can update"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que el email corresponde a un jugador del juego
        if email not in [game.white.email, game.black.email if game.black else None]:
            return Response({
                "result": False,
                "message": "Email doesn't match any player"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        game.result = otb_result
        game.finished = True
        game.save()
        
        return Response({
            "result": True,
            "message": "Game updated by player"
        }, status=status.HTTP_200_OK)

# Endpoint para actualización admin de juegos
class AdminUpdateGameAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        game_id = request.data.get('game_id')
        otb_result = request.data.get('otb_result')
        
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response({
                "result": False,
                "message": "Game does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que el usuario es el admin del torneo
        if request.user != game.round.tournament.administrative_user:
            return Response({
                "result": False,
                "message": "Only tournament admin can update"
            }, status=status.HTTP_403_FORBIDDEN)
        
        game.result = otb_result
        game.finished = True
        game.save()
        
        return Response({
            "result": True,
            "message": "Game updated by administrator"
        }, status=status.HTTP_200_OK)