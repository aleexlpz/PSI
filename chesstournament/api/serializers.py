# api/serializers.py

from rest_framework import serializers
from chess_models.models import (
    Tournament, Player, Game, 
    Round, Referee, RankingSystemClass
)
from chess_models.models.tournament import TournamentPlayers
from django.contrib.auth.models import User
from django.utils.timezone import localdate



from chess_models.constants import TournamentType, TournamentBoardType

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class RefereeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referee
        fields = '__all__'

class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = '__all__'

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'

class TournamentSerializer(serializers.ModelSerializer):
    rankingList = serializers.SerializerMethodField()
    players = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Tournament
        fields = '__all__'
        field_order = [
            'id', 'name', 'start_date', 'end_date', 'max_update_time', 
            'only_administrative', 'tournament_type', 'tournament_speed', 
            'board_type', 'win_points', 'draw_points', 'lose_points', 
            'timeControl', 'number_of_rounds_for_swiss', 'administrativeUser', 
            'referee', 'players', 'rankingList'
        ]

    def get_rankingList(self, obj):
        return [ranking.value for ranking in obj.rankingList.all()]

    def create(self, validated_data):
        players_data = validated_data.pop('players', [])
        tournament = super().create(validated_data)
        
        # Asociar jugadores al torneo a través del modelo TournamentPlayers
        registration_order = 1
        for player_data in players_data:
            if tournament.board_type == 'LIC':
                # Para torneos Lichess
                player, _ = Player.objects.get_or_create(
                    lichess_username=player_data.get('lichess_username'),
                    defaults={
                        'name': player_data.get('lichess_username'),
                        'email': f"{player_data.get('lichess_username')}@example.com"
                    }
                )
            else:
                # Para torneos OTB
                player, _ = Player.objects.get_or_create(
                    email=player_data.get('email'),
                    defaults={
                        'name': player_data.get('name'),
                        'email': player_data.get('email')
                    }
                )
            
            # Crear relación en TournamentPlayers
            TournamentPlayers.objects.create(
                tournament=tournament,
                player=player,
                registration_order=registration_order
            )
            registration_order += 1
        
        return tournament

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Opcional: incluir información básica de jugadores en la lectura
        representation['players'] = [
            {
                'name': player.name,
                'email': player.email,
                'lichess_username': player.lichess_username
            }
            for player in instance.players.all()
        ]
        return representation
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']