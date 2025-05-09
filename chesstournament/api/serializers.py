# api/serializers.py

from rest_framework import serializers
from chess_models.models import (
    Tournament, Player, Game, 
    Round, Referee, RankingSystemClass
)
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
    rankingList = serializers.SerializerMethodField()  # Campo personalizado para el ranking

    class Meta:
        model = Tournament
        fields = '__all__'
        # Define el orden de los campos (rankingList al final)
        field_order = [
            'id', 'name', 'start_date', 'end_date', 'max_update_time', 
            'only_administrative', 'tournament_type', 'tournament_speed', 
            'board_type', 'win_points', 'draw_points', 'lose_points', 
            'timeControl', 'number_of_rounds_for_swiss', 'administrativeUser', 
            'referee', 'players', 'rankingList' 
        ]

    def get_rankingList(self, obj):
        return [ranking.value for ranking in obj.rankingList.all()]

    def to_representation(self, instance):
        """Forza el orden definido en field_order."""
        representation = super().to_representation(instance)
        return {field: representation[field] for field in self.Meta.field_order if field in representation}
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']