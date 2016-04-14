from rest_framework import views, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Game
from .serializers import GameRequestSerializer, RollRequestSerializer, ScoreSerializer


def game_info(params):
    """
    Generates game information and returns it as Response

    :param params: Dict with game key
    :type params: dict

    :return: Response
    :rtype: Response
    """
    serializer = GameRequestSerializer(data=params)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    game = Game.objects.get(pk=serializer.data['game'])

    try:
        score = game.score()
    except ValidationError as e:
        return Response(e.detail, status=e.status_code)

    response = ScoreSerializer({
        'game': game.pk,
        'score': score
    })

    return Response(response.data)


class GameView(views.APIView):
    def get(self, request):
        """
        Returns game information
        Params: {game: id}
        """
        return game_info(request.query_params)

    def post(self, request):
        """
        Creates a new game
        Params: None
        """
        game = Game.objects.create()
        return game_info({'game': game.pk})


class RollView(views.APIView):
    def post(self, request):
        """
        Adds a roll to the game.
        Params {game: int, roll: int}
        """
        serializer = RollRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        game = Game.objects.get(pk=serializer.data['game'])
        try:
            game.add_roll(serializer.data['roll'])
        except ValidationError as e:
            return Response(e.detail, status=e.status_code)

        return game_info(request.data)
