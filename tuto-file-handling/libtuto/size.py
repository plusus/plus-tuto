
class InvalidSize(Exception):
    pass


class Size:
    def __init__(self, width, height):
        """
        :type width: int
        :type height: int
        """
        if not (width > 0 and height > 0):
            raise InvalidSize(
                "The Size object created is invalid: "
                "Width {}, Height {}".format(width,
                                             height))
        else:
            self._width = width
            self._height = height

    def width(self):
        return self._width

    def height(self):
        return self._height
