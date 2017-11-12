import asyncio

from pyasyncsp.port import PortRegister
from pyasyncsp.message import Message

# Change this horrific way
_global_dag = None


class Pyroutine(object):
    def __init__(self, name):
        self.name = name
        # Input and output ports
        self.inputs = PortRegister(self)
        self.outputs = PortRegister(self)
        
        self.dag = _global_dag or None
        if self.dag:
            self.dag.add_node(self)

    def __repr__(self):
        st = "{}".format(self.name)
        return st

    def __str__(self):
        st = "{}".format(self.name)
        return st

    def type_str(self):
        return type(self).__name__
    
    async def receive(self):
        messages = await self.receive_messages()
        return {k: v.value for k, v in messages.items()}

    async def receive_messages(self):
        messages = await self.inputs.receive_messages()
        for p in messages.values():
            if p.is_eos:
                raise StopAsyncIteration
        return messages

    def send_messages(self, messages):
        return self.outputs.send_messages(messages)

    def send_to_all(self, data):
        # Send
        print("Sending '{}' to all output ports".format(data))
        messages = {p: Message(data, owner=self) for p, v in self.outputs.items()}
        futures = self.outputs.send_messages(messages)
        return futures

    async def __call__(self):
        pass

    def iternodes(self):
        yield self

    @property
    def n_in(self):
        return len(self.inputs)

    @property
    def n_out(self):
        return len(self.outputs)
