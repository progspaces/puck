"""
This module provides the Actor class for running Puck programs

TODO: More information on ACTORS

For every program in Puck there is an associated actor which runs the program in its own thread.
This allows programs to be encapsulated and run concurrently alongside each other.
Each actor has a 'mailbox' which it uses to receive communication from other actors and the main thread.
By using 'receive' it can read messages from the mailbox and using 'send' can address messages to other actors' mailboxes.
It can use 'end' depending on the target function implementation to trigger joining the thread to the main thread.


Example:
    from actor import Actor, DrawingActor

    actor = Actor(target=module.run)
    actor.start()

    drawing_actor = DrawingActor(target = module.run, drawing_queue_ref = drawing_queue)
    drawing_actor.start()
"""

from collections.abc import Callable
from queue import Queue
from threading import Thread
from typing import Generic, Self, TypeVar

# Type of object sent and received by actors via mailboxes.
# In Puck, this will generally be the Message class.
M = TypeVar("M")

class Actor(Generic[M], Thread):
    def __init__(self, target: Callable[[Self], None]):
        """Initialises an actor.

        Args:
            target (a function): The function that will be triggered when you start the actor.

        Attributes:
            mailbox: a queue which other actors and the main thread can send messages to.
        """
        super().__init__(target=target, args=(self,))
        self.mailbox: Queue[M] = Queue()

    def send(self, message: M) -> None:
        self.mailbox.put(message)

    def recieve(self) -> M:
        """Get the first message from the mailbox.

        If the mailbox is empty, this hangs until a message exists.
        """
        return self.mailbox.get()
