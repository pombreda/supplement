from types import FunctionType, ClassType

from .core import AttributeGetter
from .tree import ParentNodeProvider


class Object(object):
    def __init__(self, name, node_provider):
        self.name = name
        self.node_provider = node_provider

    def get_location(self):
        node = self.get_node()
        ctx = node[0]

        if ctx == 'imported':
            name, inode = node[1], node[2]
            module = self.node_provider.get_project().get_module(inode.module)
            return module[name].get_location()
        else:
            return node[-1].lineno, self.node_provider.get_filename()

    def get_node(self):
        return self.node_provider[self.name]


class FunctionObject(Object):
    pass


class ClassObject(Object, AttributeGetter):
    def __init__(self, name, node_provider, cls):
        Object.__init__(self, name, node_provider)
        self.cls = cls

    def get_attributes(self):
        try:
            return self._attrs
        except AttributeError:
            pass

        np = ParentNodeProvider(self.get_node()[-1], self.node_provider)
        self._attrs = get_dynamic_attributes(self.cls, np)

        return self._attrs


def create_object(name, obj, node_provider):
    if type(obj) == FunctionType:
        return FunctionObject(name, node_provider)

    if type(obj) == ClassType:
        return ClassObject(name, node_provider, obj)

    return Object(name, node_provider)

def get_dynamic_attributes(obj, node_provider):
    result = {}
    for name in dir(obj):
        result[name] = create_object(name, getattr(obj, name), node_provider)

    return result