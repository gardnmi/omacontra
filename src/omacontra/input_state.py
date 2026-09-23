"""Track physical keys so remaps cannot leave translated key names stuck."""

class KeyboardState:
    def __init__(self):
        self.pressed={}
        self.keys=set()
        self.held=set()

    def press(self,code,name):
        if code in self.pressed:return self.pressed[code],False
        name=name.lower()
        if code in self.held:return name,False
        self.pressed[code]=name
        self.keys.add(name)
        return name,True

    def release(self,code):
        self.pressed.pop(code,None)
        self.held.discard(code)
        self.keys.clear()
        self.keys.update(self.pressed.values())

    def consume(self):
        # Scene changes drop held keys; autorepeat must not replay them as new presses.
        self.held.update(self.pressed)
        self.pressed.clear()
        self.keys.clear()

    def clear(self):
        # Focus loss may swallow releases, so the next press is always fresh.
        self.held.clear()
        self.pressed.clear()
        self.keys.clear()
