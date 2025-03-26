"""
Exception classes for TCP
"""


class NiryoRobotException(Exception):
    pass


class ClientNotConnectedException(Exception):
    def __init__(self, msg=None):
        if msg is None:
            msg = "You're not connected to  the robot."
        super(Exception, self).__init__(msg)


class InvalidAnswerException(Exception):
    def __init__(self, answer):
        super(Exception, self).__init__("An invalid answer has been received. Format expected: JSON.\n"
                                        + "A problem occurred with: '" + answer + "'")


class TcpCommandException(Exception):
    pass


class HostNotReachableException(Exception):
    def __init__(self):
        super(Exception, self).__init__("Unable to communicate with robot server, please verify your network.")
