class Contents():
    def __init__(self, content):
        self.content = content

class DrawingContents(Contents):
    def __init__(self, canvas_call, args, kwargs):
        self.canvas_call = canvas_call
        self.args = args
        self.kwargs = kwargs

class FunctionContents(Contents):
    def __init__(self, function):
        super().__init__()
        self.function = function


class Message():
    def __init__(self, contents):
        self.contents = contents

class Monologue(Message):
    def __init__(self, contents):
        super().__init__(contents)


class Dialogue(Message):
    def __init__(self, contents, sender):
        super().__init__(contents)
        self.contents = contents
        self.sender = sender



