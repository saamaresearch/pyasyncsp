import asyncio
import functools
from collections import OrderedDict

from .message import Message, InitMessage, FINMessage
from .connection import Connection


class Port(object):
    def __init__(self, name, node=None, optional=False):
        self.name = name
        self.node = node
        self.connections = []
        self.open = True
        self._iip = None
        #if set to True, the port must be connected
        #before the node can be used
        self.optional = optional

    @property
    def log(self):
        if self.node:
            return self.node.log.getChild(self.name)

    def set_initial_message(self, value):
        message = Message(value, owner=self.node)
        conn = InitMessage(message)
        conn.destination = self
        self.connections.append(conn)
        self._iip = True

    def kickstart(self):
        message = Message(None)
        # import ipdb; ipdb.set_trace()
        self.connections[0].queue.put_nowait(message)
        # self.send_message(message)
        # print('Kickstarting port {}'.format(self.node, self.name))

    async def receive(self):
        message = await self.receive_message()
        value = message.value
        message.drop()
        return value

    @property
    def connect_dict(self):
        return {self: [other for other in self.connections]}

    def iterends(self):
        yield from self.connections

    @property
    def is_connected(self):
        return len(self.connections) > 0

    def connect(self, other_port, size=100):
        new_conn = Connection(size=size)
        new_conn.source = self
        new_conn.destination = other_port
        self.connections.append(new_conn)
        other_port.connections.append(new_conn)

    async def send_message(self, message):
        if self.is_connected and not self.optional:
            if message.owner == self.node or message.owner == None:
                for conn in self.connections:
                    print(
                        "Sending {} from port {}".format(str(message), self.name))
                    if conn.queue.full():
                        print('Node {}: the queue between {} and {}'.format(self.node.name, conn.source.name, conn.destination.name))
                    await conn.send(message)
            else:
                print("Message {} is not owned by this Node".format(str(message), self.name))
                raise e
        else:
            if not self.optional:
                print('{} is not connected, output message will be dropped'.format(self.name))
                message.drop()
            else:
                print('Port Disconected')
    
    async def send(self, data):
        message = Message(data, owner=self.node)
        await self.send_message(message)

    async def receive_message(self, with_name=False):
        if self.is_connected:
            if self.open:
                print("Receiving at {}".format(self.name))
                done, pending = await asyncio.wait([conn.receive() for conn in self.connections], return_when=asyncio.FIRST_COMPLETED)
                # import ipdb;ipdb.set_trace()
                message = done.pop().result()
                message.decr_hopcount
                [task.cancel() for task in pending]
                print(
                    "Received {} from {}".format(message, self.name))
                # if self._iip:
                #     await self.close()
                if message.is_eos:
                    await self.close()
                    stop_message = "Stopping because {} was received".format(message)
                    print(stop_message)
                    raise StopAsyncIteration(stop_message)
                else:
                    if not with_name: 
                        return message
                    else:
                        return self.name, message
            else:
                raise StopAsyncIteration("stopp")
        else:
            # TODO: Raise appropriate error.
            pass

    ''' def callback(self):
        def wrapper(func):
            @functools.wraps(func)
            pass '''

    def __aiter__(self):
        return self

    async def __anext__(self):
        message = await self.receive_message()
        return message

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def other(self):
        for c in self.connections:
            yield c.destination


class PortRegister:
    def __init__(self, node):
        self.node = node
        self.ports = OrderedDict()

    def add(self, port):
        self.add_as(port, port.name)

    def add_as(self, port, name):
        if port.node:
            raise PortAlreadyExistingError(self.node, port)
        else:
            try:
                port.node = self.node
            except AttributeError:
                raise AttributeError(self.node, port)
            self.ports.update({name: port})

    def export(self, port, name):
        self.ports.update({name: port})

    def __getitem__(self, item):
        if item in self.ports.keys():
            return self.ports.get(item)
        else:
            raise AttributeError(self.node, str(item))

    def __getattr__(self, item):
        return self[item]

    def __iter__(self):
        return self.ports.__iter__()

    def __len__(self):
        return self.ports.__len__()

    def __str__(self):
        return "{node}: {ports}".format(node=self.node, ports=list(self.ports.items()))
    
    def __str__(self):
        return "{component}: {ports}".format(component=self.component, ports=list(self.ports.items()))

    def items(self):
        yield from self.ports.items()

    def values(self):
        return set(self.ports.values())

    def keys(self):
        return self.ports.keys()

    async def receive_messages(self):
        done, pending = await asyncio.wait([port.receive_message(with_name=True)
                                            for port in self.values()],
                                           return_when=asyncio.FIRST_COMPLETED)
        pname, message = done.pop().result()
        [task.cancel() for task in pending]
        # import ipdb; ipdb.set_trace()
        return pname, message

    async def receive_messages_from_all():
        futures = {}
        messages = {}
        for p in self.values():
            messages[p.name] = await p.receive_message()
            if p.open:
                futures[p.name] = asyncio.ensure_future(p.receive_message())
        # try as completed.. and keep creating futures..
        for k, v in futures.items():
            data = await v
            messages[k] = data
        return messages

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            messages = await self.receive_messages()
            return messages
        except StopAsyncIteration as e:
            raise StopAsyncIteration

    def send_messages(self, messages):
        futures = []
        for p in self.values():
            message = messages.get(p.name)
            futures.append(asyncio.ensure_future(p.send_message(message)))
        return futures

    def all_closed(self):
        return all([not p.open for p in self.values()])

    def iter_disconnected(self):
        for p in self.values():
            if not p.is_connected:
                yield (p.name, p)


class InputPort(Port):
    def __init__(self, *args, **kwargs):
        super(InputPort, self).__init__(*args, **kwargs)

    async def send_message(self, message):
        print("Input Only")
        raise Exception

    async def close(self):
        self.open = False
        print("closing {}".format(self.name))


class OutputPort(Port):
    def __init__(self, *args, **kwargs):
        super(OutputPort, self).__init__(*args, **kwargs)

    async def receive_message(self):
        raise OutputOnlyError(self)

    async def close(self):
        message = FINMessage()
        await self.send_message(message)
        await asyncio.wait([conn.queue.join() for conn in self.connections], return_when=asyncio.ALL_COMPLETED)
        self.open = False
        print("Closing {}".format(self.name))

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


