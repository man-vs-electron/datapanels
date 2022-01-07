from typing import Tuple, Set, Optional, Union
import time
from queue import Queue, Empty
from threading import Thread, RLock
import numpy as np
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.app import App
from kwidgets.uix.pixelatedgrid import PixelatedGrid


class GameOfLifeEngine:
    x_max: int = 100
    y_max: int = 100
    active_cells: Set[Tuple[int, int]] = set()
    offsets: Set[Tuple[int, int]] = {(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)}

    def all_neighbors(self, x: int, y: int):
        return [(x+xo, y+yo) for xo, yo in self.offsets if 0 <= (x + xo) <= self.x_max and 0 <= (y + yo) <= self.y_max]

    def is_active(self, x: int, y: int):
        return 1 if (x, y) in self.active_cells else 0

    def num_active_neighbors(self, x, y):
        return sum([self.is_active(nx, ny) for nx, ny in self.all_neighbors(x, y)])

    def clear(self):
        self.active_cells = set()

    def random(self, p: Union[float, int]):
        if p<1:
            numcells = int(self.x_max*self.y_max*p)
        else:
            numcells = int(p)
        self.active_cells.update(set([(np.random.randint(0, self.x_max), np.random.randint(0, self.y_max)) for _ in range(0, numcells)]))

    def step(self, x_max: Optional[int] = None, y_max: Optional[int] = None):
        self.x_max = self.x_max if x_max is None else x_max
        self.y_max = self.y_max if y_max is None else y_max
        new_state = set()
        for c in self.active_cells:
            active_neighbors = self.num_active_neighbors(c[0], c[1])
            if active_neighbors == 2 or active_neighbors == 3:
                new_state.update([c])
            for neighbor in self.all_neighbors(c[0], c[1]):
                if neighbor not in self.active_cells and neighbor not in new_state:
                    if self.num_active_neighbors(neighbor[0], neighbor[1]) == 3:
                        new_state.update([neighbor])
        self.active_cells = new_state
        return self.active_cells


class GameOfLifeThread:
    _gol: GameOfLifeEngine
    _q: Queue
    gol_thread: Thread
    running: bool = False
    lock = RLock()

    def __init__(self, queue_size: int = 50):
        self._q = Queue(maxsize=queue_size)
        self._gol = GameOfLifeEngine()

    def quiet_get(self):
        try:
            return self._q.get(block=False)
        except Empty:
            return None

    def get(self):
        return self._q.get()

    def clear(self):
        with self.lock:
            while not self._q.empty():
                self.quiet_get()

    def new_random(self, p: Union[float, int]):
        with self.lock:
            self._gol.clear()
            self._gol.random(p)

    def add_random(self, p: Union[float, int]):
        with self.lock:
            self._gol.active_cells = self.quiet_get() or set()
            self._gol.random(p)

    def step_loop(self):
        self.running = True
        while self.running:
            with self.lock:
                new_state = self._gol.step()
                self._q.put(new_state)

    def start(self):
        self.gol_thread = Thread(target=self.step_loop, daemon=True)
        self.gol_thread.start()


Builder.load_string('''
<GameOfLifePanel>:
    orientation: 'vertical'
    BoxLayout:
        orientation: 'horizontal'
        size_hint: 1, None
        size: 0, 50
        Button:
            text: 'Random'
        Button:
            text: 'Add 10 Random'
    PixelatedGrid:
        id: grid  
        size_hint: 1,1  
''')


class GameOfLifePanel(BoxLayout):
    pass


class GameOfLifeApp(App):
    golp: GameOfLifePanel
    golt: GameOfLifeThread

    def update(self, *args):
        new_state = self.golt.quiet_get()
        if new_state:
            self.golp.ids.grid.activated_cells = new_state

    def build(self):
        self.golt = GameOfLifeThread()
        self.golt.new_random(.2)
        self.golp = GameOfLifePanel()
        self.golt.start()
        Clock.schedule_interval(self.update, 1)
        return self.golp

if __name__ == "__main__":
    GameOfLifeApp().run()
