from contents import Contents, FunctionContents

class Message():
    __match_args__ = ("contents")
    def __init__(self, contents):
        self.contents = contents

class Monologue(Message):
    __match_args__ = ("contents")
    def __init__(self, contents):
        super().__init__(contents)


class Dialogue(Message):
    __match_args__ = ("contents", "sender")
    def __init__(self, contents, sender):
        self.contents = contents
        self.sender = sender



