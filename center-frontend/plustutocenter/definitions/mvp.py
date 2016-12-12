
class Controller:
    def getTutorials(self):
        """
        :rtype: dict[str, List[Tutorial]]
        """
        raise NotImplementedError()

    def getDoneTutorials(self):
        """
        :rtype: dict[str, list[str]]
        """
        return NotImplementedError()

    def saveDoneTutorials(self, done_tutorials):
        """
        :param done_tutorials: dict[str, list[str]]
        """
        return NotImplementedError()


class View:
    def launch(self):
        raise NotImplementedError()

    def updateDoneTutorials(self):
        """

        :return:
        """
        return NotImplementedError()
