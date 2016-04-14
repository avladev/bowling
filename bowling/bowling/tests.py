import copy
import sys

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from .score import generate, MAX_PINS, MAX_FRAMES


def get(url, data=None):
    client = Client()
    return client.get(url, data)


def post(url, data=None):
    client = Client()
    return client.post(url, data)


def generate_rolls(expected):
    return expected, [r2 for r1 in expected for r2 in r1['rolls']]


def validate_score(case, expected, frames):
    for index, frame in enumerate(frames):
        # Used for both Frame object and response from the api
        rolls = frame.rolls if hasattr(frame, 'rolls') else frame['rolls']
        number = frame.number if hasattr(frame, 'number') else frame['number']
        score = frame.score if hasattr(frame, 'score') else frame['score']
        spare = frame.spare if hasattr(frame, 'spare') else frame['spare']
        strike = frame.strike if hasattr(frame, 'strike') else frame['strike']
        completed = frame.completed if hasattr(frame, 'completed') else frame['completed']

        exp = expected[index]
        case.assertEqual(exp['rolls'], rolls, msg="Invalid rolls %d" % index)
        case.assertEqual(exp['number'], number, msg="Invalid frame number %d" % index)
        case.assertEqual(exp['score'], score, msg="Invalid score %d" % index)

        case.assertEqual(
            exp['spare'] if 'spare' in exp else False,
            spare,
            msg="Not spare %d" % index
        )

        case.assertEqual(
            exp['strike'] if 'strike' in exp else False,
            strike,
            msg="Not strike %d" % index
        )

        case.assertEqual(
            exp['completed'] if 'completed' in exp else True,
            completed,
            msg='Not completed %d' % index
        )

    case.assertEqual(len(frames), len(expected), msg='Different frame length')

DELASPORT_ROLLS = [
    {'rolls': [1, 4], 'score': 5, 'number': 1},
    {'rolls': [4, 5], 'score': 14, 'number': 2},
    {'rolls': [6, 4], 'score': 29, 'spare': True, 'number': 3},
    {'rolls': [5, 5], 'score': 49, 'spare': True, 'number': 4},
    {'rolls': [10], 'score': 60, 'strike': True, 'number': 5},
    {'rolls': [0, 1], 'score': 61, 'number': 6},
    {'rolls': [7, 3], 'score': 77, 'spare': True, 'number': 7},
    {'rolls': [6, 4], 'score': 97, 'spare': True, 'number': 8},
    {'rolls': [10], 'score': 117, 'strike': True, 'number': 9},
    {'rolls': [2, 8, 6], 'score': 133, 'spare': True, 'number': 10}
]


class ScoreTestCase(TestCase):
    def setUp(self):
        pass

    def test_delasport(self):
        """Test score generator returns expected scores from Delasport taks"""
        expected, rolls = generate_rolls(copy.deepcopy(DELASPORT_ROLLS))

        score = generate(rolls)
        validate_score(self, expected, score)

    def test_delasport_without_last_roll(self):
        uncompleted = copy.deepcopy(DELASPORT_ROLLS)
        uncompleted[-1] = {'rolls': [2, 8], 'score': 127, 'spare': True, 'completed': False, 'number': 10}
        expected, rolls = generate_rolls(uncompleted)

        score = generate(rolls)
        validate_score(self, expected, score)

    def test_uncompleted_frame(self):
        expected, rolls = generate_rolls([
            {'rolls': [10], 'score': 10, 'strike': True, 'completed': False, 'number': 1}
        ])

        score = generate(rolls)
        validate_score(self, expected, score)

    def test_two_uncompleted_frames(self):
        expected, rolls = generate_rolls([
            {'rolls': [10], 'score': 20, 'strike': True, 'completed': False, 'number': 1},
            {'rolls': [10], 'score': 30, 'strike': True, 'completed': False, 'number': 2}
        ])

        score = generate(rolls)
        validate_score(self, expected, score)

    def test_one_completed_and_two_uncompleted_frames(self):
        expected, rolls = generate_rolls([
            {'rolls': [10], 'score': 30, 'strike': True, 'completed': True, 'number': 1},
            {'rolls': [10], 'score': 50, 'strike': True, 'completed': False, 'number': 2},
            {'rolls': [10], 'score': 60, 'strike': True, 'completed': False, 'number': 3}
        ])

        score = generate(rolls)
        validate_score(self, expected, score)

    def test_all_strikes(self):
        expected, rolls = generate_rolls([
            {'rolls': [10], 'score': 30, 'strike': True, 'number': 1},
            {'rolls': [10], 'score': 60, 'strike': True, 'number': 2},
            {'rolls': [10], 'score': 90, 'strike': True, 'number': 3},
            {'rolls': [10], 'score': 120, 'strike': True, 'number': 4},
            {'rolls': [10], 'score': 150, 'strike': True, 'number': 5},
            {'rolls': [10], 'score': 180, 'strike': True, 'number': 6},
            {'rolls': [10], 'score': 210, 'strike': True, 'number': 7},
            {'rolls': [10], 'score': 240, 'strike': True, 'number': 8},
            {'rolls': [10], 'score': 270, 'strike': True, 'number': 9},
            {'rolls': [10, 10, 10], 'score': 300, 'strike': True, 'number': 10}
        ])

        score = generate(rolls)
        validate_score(self, expected, score)

    def test_all_spare(self):
        expected, rolls = generate_rolls([
            {'rolls': [1, 9], 'score': 12, 'spare': True, 'number': 1},
            {'rolls': [2, 8], 'score': 25, 'spare': True, 'number': 2},
            {'rolls': [3, 7], 'score': 39, 'spare': True, 'number': 3},
            {'rolls': [4, 6], 'score': 54, 'spare': True, 'number': 4},
            {'rolls': [5, 5], 'score': 70, 'spare': True, 'number': 5},
            {'rolls': [6, 4], 'score': 87, 'spare': True, 'number': 6},
            {'rolls': [7, 3], 'score': 105, 'spare': True, 'number': 7},
            {'rolls': [8, 2], 'score': 124, 'spare': True, 'number': 8},
            {'rolls': [9, 1], 'score': 135, 'spare': True, 'number': 9},
            {'rolls': [1, 9, 1], 'score': 146, 'spare': True, 'number': 10}
        ])

        score = generate(rolls)
        validate_score(self, expected, score)

    def test_more_then_max_pins_in_a_roll(self):
        self.assertRaises(Exception, generate, [MAX_PINS + 1])

    def test_more_then_max_pins_in_a_frame(self):
        self.assertRaises(Exception, generate, [MAX_PINS - 1, 2])

    def test_more_then_max_pins_in_a_last_frame(self):
        rolls = [
            1, 4, 4, 5, 6, 4, 5, 5, 10, 0, 1, 7, 3, 6, 4, 10,
            9, 9
        ]
        self.assertRaises(Exception, generate, rolls)

    def test_more_than_max_frames(self):
        rolls = [
            1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
            1
        ]

        self.assertRaises(Exception, generate, rolls)

    def test_strike_max_frames(self):
        rolls = [
            10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
            10, 10, 10
        ]

        self.assertRaises(Exception, generate, rolls)

    def test_spare_strike_max_frames(self):
        rolls = [
            5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
            10, 1
        ]

        self.assertRaises(Exception, generate, rolls)


class RESTTestCase(TestCase):
    def test_create_game_success(self):
        response = post(reverse('game'))

        self.assertEqual(response.status_code, 200, msg="Invalid status code %d" % response.status_code)
        self.assertIn("game", response.data, msg="No game field in response!")
        self.assertGreater(response.data['game'], 0, msg="Invalid game %d" % response.data['game'])

    def test_get_invalid_game(self):
        response = get(reverse('game'), {'game': sys.maxsize})
        self.assertGreaterEqual(response.status_code, 400, msg="Invalid status code %d" % response.status_code)
        self.assertIn("game", response.data, msg="No game error field")

    def test_delasport_rolls(self):
        game_response = post(reverse('game'))
        self.assertEqual(game_response.status_code, 200, msg="Invalid status code %d" % game_response.status_code)

        expected, rolls = generate_rolls(copy.deepcopy(DELASPORT_ROLLS))
        score = None

        for roll in rolls:
            roll_response = post(reverse('roll'), {
                'game': game_response.data['game'],
                'roll': roll
            })

            self.assertEqual(roll_response.status_code, 200, msg="Invalid status code %d" % roll_response.status_code)
            score = roll_response.data['score']

        validate_score(self, expected, score)

    def test_more_than_max_frames(self):
        game_response = post(reverse('game'))
        self.assertEqual(game_response.status_code, 200, msg="Invalid status code %d" % game_response.status_code)

        rolls = [
            1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
            1
        ]

        for index, roll in enumerate(rolls):
            roll_response = post(reverse('roll'), {
                'game': game_response.data['game'],
                'roll': roll
            })

            if index == 20:
                self.assertGreaterEqual(roll_response.status_code, 400,
                                        msg="Invalid status code %d" % roll_response.status_code)

    def test_more_then_max_pins_in_a_roll(self):
        game_response = post(reverse('game'))
        self.assertEqual(game_response.status_code, 200, msg="Invalid status code %d" % game_response.status_code)

        roll_response = post(reverse('roll'), {
            'game': game_response.data['game'],
            'roll': MAX_PINS + 1
        })

        self.assertGreaterEqual(roll_response.status_code, 400,
                                msg="Invalid status code %d" % roll_response.status_code)
        self.assertIn("roll", roll_response.data, msg="No roll error message in response")

    def test_more_then_max_pins_in_a_frame(self):
        game_response = post(reverse('game'))
        self.assertEqual(game_response.status_code, 200, msg="Invalid status code %d" % game_response.status_code)

        roll_response1 = post(reverse('roll'), {
            'game': game_response.data['game'],
            'roll': MAX_PINS - 1
        })
        self.assertEqual(roll_response1.status_code, 200, msg="Invalid status code %d" % game_response.status_code)

        roll_response2 = post(reverse('roll'), {
            'game': game_response.data['game'],
            'roll': 2
        })

        self.assertGreaterEqual(roll_response2.status_code, 400,
                                msg="Invalid status code %d" % roll_response2.status_code)
        self.assertIn("roll", roll_response2.data, msg="No roll error message in response")

    def test_all_strike(self):
        game_response = post(reverse('game'))
        self.assertEqual(game_response.status_code, 200, msg="Invalid status code %d" % game_response.status_code)

        rolls = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]

        for index, roll in enumerate(rolls):
            roll_response = post(reverse('roll'), {
                'game': game_response.data['game'],
                'roll': roll
            })

            self.assertEqual(roll_response.status_code, 200, msg="Invalid status code %d" % roll_response.status_code)

            if index == len(rolls) - 1:
                self.assertEqual(len(roll_response.data['score']), MAX_FRAMES, msg="Invalid number of frames!")
                self.assertEqual(roll_response.data['score'][9]['score'], 300, msg="Invalid score!")