from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Game


class GameSerializer(serializers.ModelSerializer):
    _links = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ['id', 'player_one', 'player_two', 'status', 'move_player_one', 'move_player_two', 'winner', '_links']

    def get__links(self, obj):
        request = self.context.get('request')
        links = {
            "self": reverse('game-detail', args=[obj.pk], request=request),
        }
        if obj.status == 'WAITING':
            links['entrar'] = reverse('game-entrar', args=[obj.pk], request=request)

        if obj.status == 'IN_PROGRESS':
            links['jogar'] = reverse('game-jogar', args=[obj.pk], request=request)

        return links