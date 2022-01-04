from typing import Union, Callable, Tuple, Set, Optional
from kivy.lang.builder import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
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


Builder.load_string('''
<GameOfLifePanel>:
    orientation: 'vertical'
    BoxLayout:
        orientation: 'horizontal'
        size_hint: 1, None
        size: 0, 50
        Button:
            text: 'Reset'
    PixelatedGrid:
        id: grid  
        size_hint: 1,1  
''')



class GameOfLifePanel(BoxLayout):
    pass


class GameOfLifeApp(App):

    def build(self):
        return GameOfLifePanel()

if __name__ == "__main__":
    GameOfLifeApp().run()
