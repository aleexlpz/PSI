# api/serializers.py
from djoser.serializers import TokenCreateSerializer

class CustomTokenCreateSerializer(TokenCreateSerializer):
    def to_representation(self, instance):
        return {'auth_token': instance.key}