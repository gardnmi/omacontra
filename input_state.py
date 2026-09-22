"""Track physical keys so remaps cannot leave translated key names stuck."""

class KeyboardState:
    def __init__(self):
        self.pressed={}
        self.keys=set()

    def press(self,code,name):
        if code in self.pressed:return self.pressed[code],False
        name=name.lower()
        self.pressed[code]=name
        self.keys.add(name)
        return name,True

    def release(self,code):
        self.pressed.pop(code,None)
        self.keys.clear()
        self.keys.update(self.pressed.values())

    def clear(self):
        self.pressed.clear()
        self.keys.clear()
