import threading
import json


class ModuleHander():
    def __init__(self):
        self._workers = {}