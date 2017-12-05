"""
Go like select on channel
"""
import asyncio
from pyasyncsp import Graph, Pyroutine
from pyasyncsp.port import InputPort, Port
from pyasyncsp.message import Message

from sample import RandomSource, Printer
from time import time
from typing import *


class AnyPortPrinter(Pyroutine):
    def __init__(self, name):
        super(AnyPortPrinter, self).__init__(name)
        self.counter = 0
        self.select_chan = {}
        # TODO: self.select_chan = Dict[str, Callable[[Message], Any]]

    async def __call__(self):
        while True:
            pname, incoming_msg = await self.inputs.receive_messages()
            
            # applying the select chan
            to_print = self.select_chan[pname](incoming_msg)
            print(f"** {self.counter}: AT time: {time()}\
                  Received {to_print} from {incoming_msg.owner.name}")
            self.counter += 1


def main():
    r1 = RandomSource('r1')
    r2 = RandomSource('r2')
    p = AnyPortPrinter('p')

    p.inputs.add(InputPort('IN1'))
    p.inputs.add(InputPort('IN2'))
    # In python select case is implemented using dicts
    p.select_chan.update({
        'IN1': lambda x: f"{x.value} at IN1",
        'IN2': lambda x: f"{x.value} at IN2",
    })
    r1.outputs.Rand_OUT.connect(p.inputs.IN1)
    # change to p.inputs.IN2 if IN2 port registered
    r2.outputs.Rand_OUT.connect(p.inputs.IN2)

    g = Graph('TrialReceiveMessages')
    g.add_node(r1)
    g.add_node(r2)
    g.add_node(p)
    g.run()

if __name__ == '__main__':
    main()