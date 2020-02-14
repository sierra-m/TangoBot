import time


class Scheduler:
    def __init__(self, limit: float, callback):
        self.limit = limit
        self.callback = callback
        self.start = 0

    def reset(self):
        self.start = time.time()

    def update(self):
        if time.time() - self.start >= self.limit:
            self.callback()
            self.reset()
