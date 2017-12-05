import asyncio
from random import random, randint

from pyasyncsp import Pyroutine
from pyasyncsp.port import InputPort, OutputPort
from pyasyncsp.message import Message
from pyasyncsp import Graph


class Printer(Pyroutine):
    def __init__(self, name):
        super(Printer, self).__init__(name)

    async def __call__(self):
        while True:
            messages = await self.receive_messages()
            show_str = " 👋 Node {} saw:\n".format(self.name) + "\n".join([str(p) for p in messages.values()])
            print(show_str)


class Adder(Pyroutine):
    """
    A Node that sums the value of the recieved signals
    """

    def __init__(self, name):
        super(Adder, self).__init__(name)
        self.inputs.add(InputPort("IN1"))
        self.inputs.add(InputPort("IN2"))
        self.outputs.add(OutputPort("ADD_OUT"))

    async def __call__(self):
        while True:
            in_messages_1 = await self.inputs.IN1.receive_message()
            print("in_message_1 = {}".format(in_messages_1))
            in_messages_2 = await self.inputs.IN2.receive_message()
            print("in_message_2 = {}".format(in_messages_1))
            summed = Message(in_messages_1.value + in_messages_2.value, owner=self)
            # print(summed)
            await self.outputs.ADD_OUT.send_message(summed)


class RandomSource(Pyroutine):
        """
        This Node generates random no signals
        """
        def __init__(self, name):
            super(RandomSource, self).__init__(name)
            self.name = name
            self.outputs.add(OutputPort("Rand_OUT"))

        async def __call__(self):
            while True:
                # generate IP containing random number
                a = Message(random(), owner=self)
                # send to the output port
                await self.outputs.Rand_OUT.send_message(a)
                await asyncio.sleep(randint(1,5))


class ManualInput(Pyroutine):
        """
        This Node generates random no signals
        """
        def __init__(self, name='manIp'):
            super(ManualInput, self).__init__(name)
            self.name = name
            self.outputs.add(OutputPort("Rand_OUT"))

        async def __call__(self):
            while True:
                # generate IP containing random number
                value = input('Enter your message')
                a = Message(value, owner=self)
                # send to the output port
                await self.outputs.Rand_OUT.send_message(a)
                await asyncio.sleep(2)


def main():
    g = Graph('demo')

    s1 = RandomSource("s1")
    s2 = RandomSource("s2")
    adder = Adder("sum_them")
    printer = Printer("show_it")
    # The printer needs an input port
    printer.inputs.add(InputPort("IN"))

    # Now we connect the components

    s1.outputs.Rand_OUT.connect(adder.inputs.IN1)
    s2.outputs.Rand_OUT.connect(adder.inputs.IN2)
    adder.outputs.ADD_OUT.connect(printer.inputs.IN)

    # Now we need to add them to a Graph instance to be able to run them.

    g.add_node(s1)
    g.add_node(s2)
    g.add_node(adder)
    g.add_node(printer)
    g.run()

if __name__ == '__main__':
    main()
