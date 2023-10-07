import time
import shutil
import termcolor
import asyncio

def line():
    return "─" * shutil.get_terminal_size()[0]

def block_line():
    return "█" * shutil.get_terminal_size()[0]

class spinner:
    def __init__(self, name):
        self.name = name
        self.spinner_task = None
        self.start = None

    def update(self):
        pass

    async def _spin(self):
        frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

        self.start = time.time()
        while True:
            for frame in frames:
                self.update()
                print("\r" + frame + " " + self.name, end='\r', flush=True)
                await asyncio.sleep(0.1)

    # async context
    async def __aenter__(self):
        self.start = time.time()
        self.spinner_task = asyncio.create_task(self._spin())
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        self.spinner_task.cancel()

def error(msg):
    return termcolor.colored(msg, "red")

def warning(msg):
    return termcolor.colored(msg, "yellow")