# api/serializers.py

from rest_framework import serializers
from chess_models.models import (
    Tournament, Player, Game, 
    Round, Referee, RankingSystemClass
)
from django.contrib.auth.models import User

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
    white = PlayerSerializer()
    black = PlayerSerializer()
    
    class Meta:
        model = Game
        fields = '__all__'

class TournamentSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True)
    rankingList = serializers.SlugRelatedField(
        many=True,
        slug_field='value',
        queryset=RankingSystemClass.objects.all()
    )
    
    class Meta:
        model = Tournament
        fields = ['id', 'name', 'tournament_type', 'tournament_speed', 'board_type', 'rankingList', 'players']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']