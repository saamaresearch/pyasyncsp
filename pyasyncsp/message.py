import asyncio

MAXHOPS = 6


class Message(object):
    def __init__(self, value, owner=None):
        self.value = value
        self._owner = owner
        self._hopcount = MAXHOPS
        print(value)

    def drop(self):
        del self

    def __str__(self):
        return f"{self.__repr__()} owned by {self.owner}, payload {self.value}, payload type {type(self.value)}"

    @staticmethod
    def decr_hopcount():
        if self._hopcount > 0:
            self._hopcount -= 1
        else:
            raise MsgMaxHopCountExceededError

    ''' @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        raise ValueError('Cannot set value')
    '''
    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        if self._owner is not None:
            raise ValueError('Curr Owner: {}, Cannot set new'.format(self.owner))
        else:
            self._owner = value
 
    @property
    def is_eos(self):
        return False

    def open(self):
        pass

    def copy(self):
        return Message(self.value, owner=None)


class InitMessage(Message):
    def __init__(self, value):
        self.value = value

    async def receive(self):
        return self.value

    async def send(self):
        raise NotImplementedError


class FINMessage(Message):
    def __init__(self):
        super(FINMessage, self).__init__(None)

    @property
    def is_eos(self):
        return True

    def __str__(self):
        return "EOS"
