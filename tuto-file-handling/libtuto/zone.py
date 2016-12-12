class Zone:
    """
    Zone with defined boundaries
    """

    def topLeft(self):
        """
        :rtype: (int, int)
        """
        raise NotImplementedError()

    def bottomRight(self):
        """
        :rtype: (int, int)
        """
        raise NotImplementedError()

    def center(self):
        """
        :rtype: (int, int)
        """
        raise NotImplementedError()


class RectangleZone:
    def __init__(self, topLeftPoint, bottomRightPoint):
        self._topLeftPoint = topLeftPoint
        self._bottomRightPoint = bottomRightPoint

    def topLeft(self):
        return self._topLeftPoint

    def bottomRight(self):
        return self._bottomRightPoint

    def center(self):
        point = [0, 0]
        for i in range(2):
            point[i] = self._topLeftPoint[i] + \
                (self._bottomRightPoint[i] - self._topLeftPoint[i]) // 2
        return point


def zoneFactory(shape, data):
    """
    Factory method for instantiation of zone objects.
    :param shape: Shape string descriptor
    :param data: List of data to be used for instantiation
    :return: Shape object
    :rtype: Zone
    """
    return {
        "rectangle": lambda: RectangleZone(tuple(data[0:2]), tuple(data[2:4]))
    }.get(shape)()

