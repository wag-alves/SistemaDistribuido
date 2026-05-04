from django.contrib import admin
from .models import Player

# Isso faz o 'player_service' aparecer na lista do admin
admin.site.register(Player)