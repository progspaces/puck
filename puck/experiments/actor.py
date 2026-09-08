from threading import Thread
from typing import Self

class Actor(Thread):
    def __init__(self, target, drawing_actor:Self):
        super().__init__(target=target, args=(self, drawing_actor))
        self.unread_messages:list[tuple[Actor, dict]] = []

    def send_to(self, recipient:Self, message:dict): ## push to this queue
        recipient.unread_messages.append((self, message))

    def read(self) -> tuple[Self, dict]:  ## pop of our own
        while len(self.unread_messages) == 0:
            pass
        return self.unread_messages.pop(0)

    def end(self):
        self.unread_messages.append((None, {"type": "kill"}))

