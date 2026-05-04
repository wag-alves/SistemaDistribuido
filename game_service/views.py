from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Game
from .serializers import GameSerializer
import random
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

CARTAS = [
    {"nome": "Mago",      "peso": 10, "emoji": "🧙"},
    {"nome": "Dragão",    "peso": 9,  "emoji": "🐉"},
    {"nome": "Cavaleiro", "peso": 7,  "emoji": "⚔️"},
    {"nome": "Fênix",     "peso": 6,  "emoji": "🔥"},
    {"nome": "Arqueiro",  "peso": 5,  "emoji": "🏹"},
    {"nome": "Lobo",      "peso": 4,  "emoji": "🐺"},
    {"nome": "Goblin",    "peso": 3,  "emoji": "👺"},
    {"nome": "Rato",      "peso": 1,  "emoji": "🐀"},
]

NOMES_CARTAS = [c["nome"] for c in CARTAS]
PESO_POR_NOME = {c["nome"]: c["peso"] for c in CARTAS}

@method_decorator(csrf_exempt, name='dispatch')
class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def create(self, request, *args, **kwargs):
        player_one_id = request.data.get('player_one')
        if not player_one_id:
            return Response({'erro': 'Informe player_one.'}, status=status.HTTP_400_BAD_REQUEST)

        game = Game.objects.create(player_one_id=player_one_id, status=Game.STATUS_WAITING)
        serializer = self.get_serializer(game, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='entrar')
    def entrar(self, request, pk=None):
        """Player dois entra na partida."""
        game = self.get_object()

        if game.status != Game.STATUS_WAITING:
            return Response({'erro': 'Esta partida não está mais aguardando jogadores.'}, status=status.HTTP_400_BAD_REQUEST)

        player_two_id = request.data.get('player_two')
        if not player_two_id:
            return Response({'erro': 'Informe player_two.'}, status=status.HTTP_400_BAD_REQUEST)

        if str(game.player_one_id) == str(player_two_id):
            return Response({'erro': 'Você não pode entrar na sua própria partida.'}, status=status.HTTP_400_BAD_REQUEST)

        game.player_two_id = player_two_id
        game.status = Game.STATUS_IN_PROGRESS
        game.save()

        serializer = self.get_serializer(game, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='jogar')
    def jogar(self, request, pk=None):
        """
        Jogador submete sua jogada.
        Body: { "player_id": 1 }  — a carta é sorteada pelo servidor.
        Quando os dois jogadores tiverem jogado, o duelo é resolvido automaticamente.
        """
        game = self.get_object()

        if game.status != Game.STATUS_IN_PROGRESS:
            return Response({'erro': 'Partida não está em andamento.'}, status=status.HTTP_400_BAD_REQUEST)

        player_id = str(request.data.get('player_id', ''))
        if not player_id:
            return Response({'erro': 'Informe player_id.'}, status=status.HTTP_400_BAD_REQUEST)

        is_p1 = str(game.player_one_id) == player_id
        is_p2 = str(game.player_two_id) == player_id

        if not is_p1 and not is_p2:
            return Response({'erro': 'Você não pertence a esta partida.'}, status=status.HTTP_403_FORBIDDEN)

        # Evita jogar duas vezes
        if is_p1 and game.move_player_one:
            return Response({'erro': 'Você já jogou. Aguardando oponente...', 'status': game.status}, status=status.HTTP_400_BAD_REQUEST)
        if is_p2 and game.move_player_two:
            return Response({'erro': 'Você já jogou. Aguardando oponente...', 'status': game.status}, status=status.HTTP_400_BAD_REQUEST)

        carta = random.choice(NOMES_CARTAS)

        if is_p1:
            game.move_player_one = carta
        else:
            game.move_player_two = carta

        game.save()

        # Se ambos jogaram, resolve o duelo
        if game.move_player_one and game.move_player_two:
            return self._resolver_duelo(game, player_id)

        return Response({'mensagem': 'Jogada registrada! Aguardando oponente...', 'sua_carta': carta})

    def _resolver_duelo(self, game, player_id_solicitante):
        peso_p1 = PESO_POR_NOME[game.move_player_one]
        peso_p2 = PESO_POR_NOME[game.move_player_two]

        if peso_p1 > peso_p2:
            game.winner = game.player_one
        elif peso_p2 > peso_p1:
            game.winner = game.player_two
        # empate: winner permanece None

        game.status = Game.STATUS_FINISHED
        game.save()

        # Determina resultado do ponto de vista de quem chamou
        is_p1 = str(game.player_one_id) == str(player_id_solicitante)
        minha_carta   = game.move_player_one if is_p1 else game.move_player_two
        carta_inimiga = game.move_player_two if is_p1 else game.move_player_one

        if game.winner is None:
            resultado = "Empate!"
        elif str(game.winner_id) == str(player_id_solicitante):
            resultado = "Você Venceu! 🏆"
        else:
            resultado = "Você Perdeu! 💀"

        return Response({
            'voce_jogou': minha_carta,
            'oponente_jogou': carta_inimiga,
            'resultado': resultado,
            'status': game.status,
        })