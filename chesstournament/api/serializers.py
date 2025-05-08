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
    rankingList = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = Tournament
        fields = '__all__'

    def create(self, validated_data):
        ranking_list_data = validated_data.pop('rankingList', [])
        tournament = super().create(validated_data)

        # Ensure all ranking systems exist, then add them
        for ranking_value in ranking_list_data:
            ranking_obj, _ = RankingSystemClass.objects.get_or_create(value=ranking_value)
            tournament.rankingList.add(ranking_obj)

        return tournament
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']