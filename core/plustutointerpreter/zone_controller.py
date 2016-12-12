from libtuto.tutorial import TutorialStep

class StepController:
    """
    Controller for the steps used in tutorials
    """
    def __init__(self, steps):
        """
        :type steps: List[TutorialStep]
        """
        self._steps = steps
        self._index = 0
        self._done = False

    def reset(self):
        self._index = 0
        self._done = False

    def is_done(self):
        return self._done

    def get_step(self):
        """
        :rtype: TutorialStep
        """
        return self._steps[self._index]

    def has_previous(self):
        return self._index > 0

    def has_next(self):
        return self._index < len(self._steps) - 1

    def next(self):
        if self.has_next():
            self._index += 1
        else:
            self._done = True
            raise StopIteration()

    def previous(self):
        if self.has_previous():
            self._index -= 1
        else:
            raise StopIteration()
