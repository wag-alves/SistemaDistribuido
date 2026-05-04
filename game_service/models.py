from django.db import models
from player_service.models import Player

class Game(models.Model):
    STATUS_WAITING    = 'WAITING'     # Aguardando player_two entrar
    STATUS_IN_PROGRESS = 'IN_PROGRESS' # Ambos conectados, aguardando jogadas
    STATUS_FINISHED   = 'FINISHED'

    player_one = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='games_as_p1')
    player_two = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='games_as_p2', null=True, blank=True)

    status = models.CharField(max_length=20, default=STATUS_WAITING)

    # Cartas jogadas por cada um (null = ainda não jogou)
    move_player_one = models.CharField(max_length=50, null=True, blank=True)
    move_player_two = models.CharField(max_length=50, null=True, blank=True)

    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='wins')

    def __str__(self):
        return f"Game #{self.pk} [{self.status}]"