"""Local Hyprland window integration, extracted from Hyprsplitter (MIT).
See THIRD_PARTY/hyprsplitter-LICENSE.txt.
"""
import json
import os
import socket

class Hyprland:
    def __init__(self):
        signature = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
        runtime = os.environ.get("XDG_RUNTIME_DIR")
        if not signature or not runtime:
            raise RuntimeError("Run this inside your Hyprland session.")
        self.path = f"{runtime}/hypr/{signature}/.socket.sock"

    def request(self, command, parse=False):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(2)
            connection.connect(self.path)
            connection.sendall((("j/" if parse else "/") + command).encode())
            data = bytearray()
            while chunk := connection.recv(65536):
                data.extend(chunk)
        result = data.decode()
        if parse:
            return json.loads(result)
        if result.strip() != "ok":
            raise RuntimeError(f"Hyprland rejected {command}: {result}")
        return result

    def run(self, *actions):
        self.request("eval " + "; ".join(f"hl.dispatch({action})" for action in actions))

    def focus(self, address):
        self.run(f'hl.dsp.focus({{window="address:{address}"}})')
