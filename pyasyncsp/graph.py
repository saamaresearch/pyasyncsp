import asyncio
from .pyroutine import Pyroutine


class Graph(Pyroutine):
    def __init__(self, name, workdir=None):
        super(Graph, self).__init__(name)
        self._nodes = set()
        self._name = name
        self.workdir = workdir or './'
        print("Created DAG {} with workdir {}".format(self.name, self.workdir))

    @property
    def workdir(self):
        if self._workdir:
            return self._workdir
        else:
            return ""

    @workdir.setter
    def workdir(self, dir):
        self._workdir = dir

    def connect(self, port1, port2):
        # Add nodes that are not in the node list
        print("DAG {}: Connecting {} to {}".format(self.name, port1, port2))
        for port in [port1, port2]:
            try:
                # Add log to every component
                port.component.dag = self
                if not self.hasnode(port.component):
                    self._nodes.add(port.component)
            except:
                raise ValueError('Port {} does not exist'.format(port))
                print("Port {} does not exist".format(port))
        port1.connect(port2)
        # self._arcs.update(port1.connect_dict)

    def set_initial_message(self, port, value):
        port.set_initial_message(value)

    def set_kickstarter(self, port):
        port.kickstart()

    def add_node(self, node):
        node.dag = self
        
        self._nodes.add(node)
        return node

    def hasarc(self, node1, node2, outport, inport):
        return node1 in self._arcs and {node2: (outport, inport)} in self._arcs[node1]

    def hasnode(self, node):
        return node in self._nodes

    def disconnect(self, node1: Pyroutine, node2: Pyroutine):
        # TODO implement disconnect
        pass

    def iternodes(self) -> Pyroutine:
        for node in self._nodes:
            yield from node.iternodes()

    def iterarcs(self):
        for source in self.iternodes():
            for port in list(source.outputs.values()):
                for dest in port.iterends():
                    yield (port, dest)

    def adjacent(self, node):
        if node in self._arcs:
            yield from self._arcs[node]
        else:
            return

    def run(self):
        # Add code to the repository
        loop = asyncio.get_event_loop()
        self.loop = loop
        print('Starting DAG')
        print('has following nodes {}'.format(list(self.iternodes())))
        try:
            tasks = [loop.create_task(node()) for node in self.iternodes()]
            loop.run_until_complete(asyncio.gather(*tasks))
        except StopAsyncIteration as e:
            print('Received EOS')
        except Exception as e:
            print(e)
            print('Stopping DAG by cancelling scheduled tasks')
            if not loop.is_closed():
                task = asyncio.Task.all_tasks()
                future = asyncio.gather(*(task))
                future.cancel()
        finally:
            if loop.is_running():
                loop.stop()
                print('Stopping DAG')
            print('Stopped')
