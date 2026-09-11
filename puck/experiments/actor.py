from threading import Thread
from typing import Self
from queue import Queue

class Actor(Thread):
    def __init__(self, target):
        super().__init__(target=target, args=(self,))
        self.unread_messages:list[tuple[Self, dict]] = []

    def send_to(self, recipient:Self, message:dict): ## push to this queue
        recipient.unread_messages.append((self, message))

    def read(self) -> tuple[Self, dict]:  ## pop of our own
        while len(self.unread_messages) == 0:
            pass
        return self.unread_messages.pop(0)

    def read_only_message(self, message):
        self.unread_messages.append((None, message))

    def end(self):
        self.read_only_message({"type": "kill"})

