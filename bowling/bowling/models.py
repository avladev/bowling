from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from rest_framework.exceptions import ValidationError

from .score import MAX_PINS, generate


class Game(models.Model):
    def add_roll(self, roll):
        """
        Adds a roll to a game

        :param roll: Number of pins knocked
        :type roll: int

        :return: List of Frames for the game
        :rtype: list[Frame]
        """
        score = self.score(roll)
        self.rolls.create(roll=roll)

        return score

    def score(self, include=None):
        """
        Generates all the frames for the game

        :param include: Add additional roll to the rolls in DB
        :type include: int

        :return: List of Frames for the game
        :rtype: list[Frame]
        """
        rolls = list(self.rolls.values_list('roll', flat=True))

        if include:
            rolls.append(include)

        try:
            score = generate(rolls)
        except Exception as e:
            raise ValidationError({'roll': str(e)})

        return score

    def __str__(self):
        return 'Game ' + str(self.pk)


class Roll(models.Model):
    game = models.ForeignKey(Game, related_name='rolls')
    roll = models.IntegerField(validators=[
        MinValueValidator(0),
        MaxValueValidator(MAX_PINS)
    ])

    def __str__(self):
        return 'Game ' + str(self.game.pk) + ' roll ' + str(self.roll)
