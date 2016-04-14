from rest_framework import serializers
from rest_framework.compat import MinValueValidator, MaxValueValidator

from .models import Game
from .score import MAX_PINS, MAX_FRAMES


class ValidateGameMixin(object):
    def validate_game(self, game):
        if Game.objects.filter(pk=game).exists():
            return game

        raise serializers.ValidationError("Game does not exist!")


class GameRequestSerializer(ValidateGameMixin, serializers.Serializer):
    game = serializers.IntegerField()


class RollRequestSerializer(ValidateGameMixin, serializers.Serializer):
    game = serializers.IntegerField()
    roll = serializers.IntegerField(validators=(
        MinValueValidator(0),
        MaxValueValidator(MAX_PINS)
    ))


class FrameSerializer(serializers.Serializer):
    rolls = serializers.ListField(child=serializers.IntegerField(), read_only=True)
    number = serializers.IntegerField(read_only=True, validators=[
        MinValueValidator(1),
        MaxValueValidator(MAX_FRAMES)
    ])
    strike = serializers.BooleanField(read_only=True)
    spare = serializers.BooleanField(read_only=True)
    score = serializers.IntegerField(read_only=True)
    completed = serializers.BooleanField(read_only=True)


class ScoreSerializer(serializers.Serializer):
    game = serializers.IntegerField(read_only=True)
    score = FrameSerializer(many=True, read_only=True)
