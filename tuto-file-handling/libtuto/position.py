class Position:
    def topLeft(self):
        """
        :rtype: (int, int)
        """
        raise NotImplementedError()

    def width(self):
        """
        :rtype: int | None
        """
        raise NotImplementedError()

    def height(self):
        """
        :rtype: int | None
        """
        raise NotImplementedError()


class PointPosition:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def topLeft(self):
        return self._x, self._y

    def width(self):
        return None

    def height(self):
        return None


def positionFactory(descriptor, data):
    """
    Factory method for a text position object.
    :param descriptor: Descriptor of the position type
    :param data: List of data to be used for instantiation
    :return: Text position object
    :rtype: Position
    """
    return {
        "point": lambda: PointPosition(*data)
    }.get(descriptor)()
