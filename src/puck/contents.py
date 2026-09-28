
from functools import partial

class Contents():
    __match_args__ = ("content")
    def __init__(self, content):
        self.content = content

class FunctionContents(Contents):
    __match_args__ = ("function_call", "args", "kwargs")
    def __init__(self, function_call, args, kwargs):
        self.function_call = partial(function_call, args, kwargs)
