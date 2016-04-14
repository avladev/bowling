MAX_PINS = 10
MAX_FRAMES = 10


def generate(rolls):
    """
    Generates a list of frames for a given rolls

    :param rolls: List of rolls
    :type rolls: list[int]

    :rtype: list[Frame]
    """
    frames = []
    rolls_count = len(rolls)
    frame = Frame(1)

    for index, roll in enumerate(rolls):
        if frame.end_frame and frame.completed:
            if not frame.strike and not frame.spare and index <= rolls_count - 1:
                raise Exception('Frames exceeded')
            continue

        frame = Frame(frame.number + 1, frame.score) if frame.rolls_completed else frame
        frame.add_roll(roll)

        try:
            if frame.spare:
                frame.add_roll(rolls[index + 1])

            if frame.strike:
                frame.add_roll(rolls[index + 1])
                frame.add_roll(rolls[index + 2])

        except IndexError:
            pass

        if frame.rolls_completed or index == rolls_count - 1:
            # Append the frame in result if the rolls for the frame are completed
            # or it's a last frame for the given rolls
            frames.append(frame)
            continue

    return frames


class Frame(object):
    def __init__(self, number, prev_score=0):
        """
        :param number: The frame number in the game 1-MAX_FRAMES
        :type number: int

        :param prev_score: Score from the previous frame
        :type prev_score: int
        """
        if number > MAX_FRAMES:
            raise Exception("You cannot have more than a %d frames in a game!" % MAX_FRAMES)

        self._number = number  # Frame number 1-MAX_FRAMES
        self._end_frame = number == MAX_FRAMES  # Is it the end frame = MAX_FRAMES

        self._rolls = []  # List of rolls in current frame
        self._rolls_sum = 0
        self._rolls_count = 0

        self._next_rolls = []  # List of rolls that summed in this frame but they are from next frames
        self._next_rolls_sum = 0
        self._next_rolls_count = 0

        self._strike = False  # Does it have strike in this frame
        self._spare = False  # Does it have spare in this frame

        self._prev_score = prev_score  # The score from previous frame
        self._score = None  # Score of the frame (!not the rolls)
        self._completed = False  # Frame is completed when no information is required for next rolls
        self._rolls_completed = False

    @property
    def number(self):
        """
        Returns frame number in the game
        :rtype: int
        """
        return self._number

    @property
    def rolls(self):
        """
        Returns the rolls in current frame [first, second]
        :rtype: list[int]
        """
        return self._rolls

    @property
    def strike(self):
        """
        Is there a strike in the frame
        :rtype: bool
        """
        return self._strike

    @property
    def spare(self):
        """
        Is there a spare in the frame
        :rtype: bool
        """
        return self._spare

    @property
    def score(self):
        """
        Current score of the frame
        :rtype: int
        """
        return self._score

    @property
    def completed(self):
        """
        Returns true if frame does not need any additional rolls to compute a final score
        :rtype: bool
        """
        return self._completed

    @property
    def rolls_completed(self):
        """
        Returns true if frame cannot accept more rolls
        :rtype: bool
        """
        return self._rolls_completed

    @property
    def end_frame(self):
        """
        Is this frame is a last frame of the game
        :rtype: bool
        """
        return self._end_frame

    def add_roll(self, roll):
        """
        Adds a roll to a frame.
        If the roll belongs to another frame (eg. strike or spare)

        :param roll: Number of pins knocked
        :type roll: int

        :rtype: None
        """
        if self.completed:
            raise Exception('You cannot add a roll to a completed frame!')

        if roll > MAX_PINS:
            raise Exception("Invalid pins!")

        if not self.end_frame and (self.strike or self.spare):
            # If the roll belongs to next frame
            self._next_rolls.append(roll)
            self._next_rolls_sum = sum(self._next_rolls)
            self._next_rolls_count = len(self._next_rolls)
        else:
            # If the roll belongs to this frame
            if self._rolls_sum + roll > self._calculate_rolls_sum_max():
                raise Exception('Exceeded maximum pins for a frame!')

            self._rolls.append(roll)
            self._rolls_sum = sum(self._rolls)
            self._rolls_count = len(self._rolls)

        self._strike = self._rolls_count >= 1 and self._rolls[0] == MAX_PINS
        self._spare = self._rolls_count >= 2 and self._rolls[0] + self._rolls[1] == MAX_PINS
        self._score = self._prev_score + self._rolls_sum + self._next_rolls_sum

        self._completed = self._calculate_completed()
        self._rolls_completed = self._calculate_rolls_completed()

    def _calculate_completed(self):
        """
        Calculates where a Frame is completed.

        Completed frame is a frame which no roll information is needed
         to be able to calculate its final score

        :rtype: bool
        """
        if self.strike and self.end_frame and self._rolls_count == 3:
            # We have a strike in the MAX_FRAMES-th frame so we expect 3 rolls
            return True
        elif self.strike and not self.end_frame and self._next_rolls_count == 2:
            # We have a strike and expect 2 rolls from next frames
            return True
        elif self.spare and self.end_frame and self._rolls_count == 3:
            # We have a spare in the MAX_FRAMES-th frame so we expect 3 rolls in this one
            return True
        elif self.spare and self._next_rolls_count == 1:
            # We have a spare and expect 1 roll from next frame
            return True
        elif not self.strike and not self.spare and self._rolls_count == 2:
            # No spare or strike in this frame we need 2 rolls
            return True
        else:
            return False

    def _calculate_rolls_sum_max(self):
        """
        This function calculates the max sum of rolls the user can reach
        :rtype: int
        """
        if self.end_frame and self._rolls_sum == MAX_PINS * 2:
            # This handles the case where we have 2 strikes in last frame
            # and last max option is another strike
            return MAX_PINS * 3
        elif self.end_frame and self._rolls_sum == MAX_PINS:
            # This handles the case where we have a strike on first roll or spare in first 2 rolls
            # and last max option is another strike
            return MAX_PINS * 2
        else:
            # Everything else
            return MAX_PINS

    def _calculate_rolls_completed(self):
        """
        Returns true if Frame have all rolls added
        :rtype: bool
        """
        if self.end_frame and (self.strike or self.spare):
            # On the end frame if we have strike or spare we have max 3 rolls
            return self._rolls_count == 3
        elif not self.end_frame and self.strike:
            # On any frame except end one if he have strike we cannot accept another
            return self._rolls_count == 1
        else:
            # Otherwise we expect 2 rolls
            return self._rolls_count == 2
