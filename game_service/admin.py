from django.contrib import admin
from .models import Game

# Isso faz o 'player_service' aparecer na lista do admin
admin.site.register(Game)