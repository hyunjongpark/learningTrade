class BaseService():
    def __init__(self):
        self.items = {}

    def clear(self):
        self.items.clear()

    def register(self, name, value):
        self.items[name] = value

    def get(self, name):
        return self.items[name]

    def remove(self, name):
        del self.items[name]


class Configurator(BaseService):
    def __init__(self):
        self.items = {}

    def update(self, name, value):
        self.items[name] = value


class Services(BaseService):
    def register(self, name, ref):
        self.items[name] = ref


services = Services()
