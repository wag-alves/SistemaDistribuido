from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Player

class PlayerSerializer(serializers.ModelSerializer):
    _links = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ['id', 'username', 'level', '_links'] 

    def get__links(self, obj):
        request = self.context.get('request')
        return {
            "self": reverse('player-detail', args=[obj.pk], request=request),
            "partidas": reverse('game-list', request=request) + f"?player={obj.pk}"
        }