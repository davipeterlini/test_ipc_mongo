import bson
import pymongo as mongo

from Ipc import IpcMessage

EXAMPLE_MESSAGE = 0

class ExampleMessage(IpcMessage):
    def __init__(self, a=None, b=None, c=None):
        IpcMessage.__init__(self)
        self.set_a(a)
        self.set_b(b)
        self.set_c(c)

    def get_type(self):
        return EXAMPLE_MESSAGE

    def get_a(self):
        return self.a

    def set_a(self, a):
        self.a = a

    def get_b(self):
        return self.b

    def set_b(self, b):
        self.b = b

    def get_c(self):
        return self.c

    def set_c(self, c):
        self.c = c

    def from_dict(self, data):
        self.set_a(data["a"])
        self.set_b(data["b"])
        self.set_c(data["c"])

    def to_dict(self):
        data = {}
        data["a"] = str(self.get_a())
        data["b"] = str(self.get_b())
        data["c"] = str(self.get_c())
        return data

    def __str__(self):
        s = "ExampleMessage\n"
        s += "  a: " + str(self.get_a()) + "\n"
        s += "  b: " + str(self.get_b()) + "\n"
        s += "  c: " + str(self.get_c()) + "\n"
        return s
