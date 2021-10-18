from src.modules.module import Module
from src.device import Device


class Cisco(Module):
    def __init__(self, device: Device = None, *args, **kwargs):
        super().__init__(device, *args, **kwargs)

    def worker(self):
        return {"msg": f"hello from module Cisco", "bestKey": {"a": "b", "c": "d"}, "timestamp": 1234}