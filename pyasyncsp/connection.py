import asyncio


class Connection():
    def __init__(self, size=4):
        self.queue = asyncio.Queue(maxsize=size)
        self.source = None
        self.destination = None

    async def receive(self):
        if self.source:
            packet = await self.queue.get()
            self.queue.task_done()
            return packet

    async def send(self, packet):
        if self.destination:
            if self.destination.open:
                await self.queue.put(packet)
            else:
                print("Port Closed.")