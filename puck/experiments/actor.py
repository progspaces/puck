from threading import Thread
from typing import Self
from tkinter import Canvas

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

    def read_only_message(self, message):
        self.unread_messages.append((None, message))

    def end(self):
        self.read_only_message({"type": "kill"})
        self.join()


class DrawingActor(Thread):
    def __init__(self, target, canvas:Canvas):
        super().__init__(target=target, args=(self, canvas))
        self.unread_messages:list[tuple[Actor, dict]] = []

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
        self.join()
