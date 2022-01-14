from typing import Tuple, Set, Optional, Union
import numpy as np
from kivy.lang.builder import Builder
from kivy.properties import ListProperty
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


Builder.load_string('''
<GameOfLifePanel>:
    orientation: 'vertical'
    BoxLayout:
        orientation: 'horizontal'
        size_hint: 1, None
        size: 0, 50
        Button:
            text: 'Random'
            on_press: root.new_random(.2)
        Button:
            text: 'Add 100 Random'
            on_press: root.gol.random(100)
    PixelatedGrid:
        id: grid  
        size_hint: 1,1  
        activated_color: root.activated_color
''')


class GameOfLifePanel(BoxLayout):
    gol: GameOfLifeEngine
    activated_color = ListProperty([0, 1, 1, 1])
    initialized = False
    update_event = None

    def __init__(self, **kwargs):
        super(GameOfLifePanel, self).__init__(**kwargs)
        self.gol = GameOfLifeEngine()

    def gol_update(self, *args):
        new_state = self.gol.step(self.ids.grid.visible_width(), self.ids.grid.visible_height())
        self.ids.grid.activated_cells = new_state

    def new_random(self, p: Union[float, int], *args):
        self.gol.clear()
        self.gol.random(p)

    def dp_stop(self):
        if self.update_event is not None:
            self.update_event.cancel()
            self.update_event = None

    def dp_start(self):
        if not self.initialized:
            self.gol.random(.2)
            self.initialized = True
        self.update_event = Clock.schedule_interval(self.gol_update, .1)


class GameOfLifeApp(App):

    def build(self):
        panel = GameOfLifePanel()
        panel.dp_start()
        return panel


if __name__ == "__main__":
    GameOfLifeApp().run()
