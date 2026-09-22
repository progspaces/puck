from threading import Thread
from typing import Self
from queue import Queue

class Actor(Thread):
    """ For every program in Puck there is an associated actor which runs the program in its own thread.
    This allows programs to be encapsulated and run concurently along side each other.
    Each actor has a 'mailbox' which it uses to recieve communication from other actors and the main thread.
    By using 'recieve' it can read messages from the mailbox and using 'send' can address messages to other actors' mailboxes.
    It can use 'end' depending on the target function implementation to trigger joining the thread to main thread.
    """

    def __init__(self, target):
        """ Initialises an actor.
        Args:
            target (a function name): The function that will be triggered when you start the actor.
            
        Attributes:
            mailbox (Queue): a queue which other actors and the main thread can send messages to.
        """
        super().__init__(target=target, args=(self,))
        self.mailbox: Queue = Queue()

    def send(self: Self, message):
        """
        Sends message to the actor in actor.send()

        Args:
            self (Self): actor
            message (_type_): any object
        """
        self.mailbox.put(message)

    def recieve(self):
        """Read messages that are in the mailbox

        Returns:
            obj: whatever the message is, completely arbitrary object.
        """
        return self.mailbox.get()

    def end(self):
        """Sends the 'kill' message to its own mailbox.
        """
        self.send("kill")
