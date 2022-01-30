""" DataPanels implementation of Conway's Game of Life

See https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life for details about
the game.

"""
from typing import Tuple, Set, Optional, Union, List
import numpy as np
from kivy.lang.builder import Builder
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.app import App
from kwidgets.uix.pixelatedgrid import PixelatedGrid


class GameOfLifeEngine:
    """ Game of Life implementation

    This class implements the rules and mechanism for computing successive states.  No graphical operations are
    conducted.

    The current state of the grid is stored in active_cells.  This set of tuples contains the X,Y coordinates of all
    the live cells.

    The key idea here is that the state is simply the currently live cells.  If a cell is going to change state, it
    either has to be a live cell or adjecent to a live cell.  So only dealing with currently live cells and their
    neighbors reduces the amount of computation that has to be performed.

    """
    x_max: int = 100
    y_max: int = 100
    active_cells: Set[Tuple[int, int]] = set()
    offsets: Set[Tuple[int, int]] = {(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)}

    def all_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """ Get a list of the coordinates of all the neighbors of some cell.

        The coordinates (q,r) for the neighbors must be in the range (0<=q<=x_max, 0<=r<=y_max).  Any coordinates
        outside this range are ignored.  So if the neighbors for a cell at the edge of the board are rquested, only
        neighbors that are on the board are returned.

        :param x:
        :param y:
        :return: List of neighbors
        """
        return [(x+xo, y+yo) for xo, yo in self.offsets if 0 <= (x + xo) <= self.x_max and 0 <= (y + yo) <= self.y_max]

    def is_active(self, x: int, y: int) -> int:
        """ Whether the indicated cell is alive

        :param x:
        :param y:
        :return: 1 if it is alive, 0 otherwise
        """
        return 1 if (x, y) in self.active_cells else 0

    def num_active_neighbors(self, x, y) -> int:
        """ How many neighbors of (x,y) are alive

        :param x:
        :param y:
        :return:
        """
        return sum([self.is_active(nx, ny) for nx, ny in self.all_neighbors(x, y)])

    def clear(self):
        """ Set active_cells to an empty set, indicating that no cells are alive

        :return:
        """
        self.active_cells = set()

    def random(self, p: Union[float, int]):
        """ Set some cells randomly to being alive

        :param p: If in the range of 0 to 1, select that proportion of cells to make alive.  Otherwise treat as the
        number of cells to make alive.
        :return:
        """
        if p<1:
            numcells = int(self.x_max*self.y_max*p)
        else:
            numcells = int(p)
        self.active_cells.update(set([(np.random.randint(0, self.x_max), np.random.randint(0, self.y_max)) for _ in range(0, numcells)]))

    def step(self, x_max: Optional[int] = None, y_max: Optional[int] = None):
        """ Update the state.

        Run one generation.

        :param x_max: The largest x value for the visible board
        :param y_max: The largest y value for the visible board
        :return: In addition to setting the local active_cells variable, return the set of active cells.
        """
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
        background_color: root.background_color
        grid_color: root.grid_color
        cell_length: root.cell_length
''')


class GameOfLifePanel(BoxLayout):
    """ The Kivy panel that displays the Game of Life, along with some controls.

    The user can randomize the screen with a button press, or add random live cells with another button press.

    Key Properties:
    * update_rate: number of seconds between each generation
    * random_cell_count: Either percentage of cells to make alive or the number of cells to make alive when randomizing.
    * background_color - RGBA list for the inactive cell color
    * grid_color - RGBA for the grid lines
    * activated_color - RGBA for the active cell color
    * cell_length - the length of the side of a cell (essentially cell size)

    """
    gol: GameOfLifeEngine
    activated_color = ListProperty([0, 1, 1, 1])
    background_color = ListProperty([0, 0, 0, 1])
    grid_color = ListProperty([47/255, 79/255, 79/255, 1])
    cell_length = NumericProperty(10)
    initialized = False
    update_event = None
    update_rate = NumericProperty(0.1)
    random_cell_count = NumericProperty(0.2)

    def __init__(self, **kwargs):
        """ Create a new GameOfLifePanel instance

        Creates a new engine instance.

        :param kwargs:
        """
        super(GameOfLifePanel, self).__init__(**kwargs)
        self.gol = GameOfLifeEngine()

    def gol_update(self, *args):
        """ Move the engine ahead one generation, passing in the current size of the grid

        :param args: Unused
        :return:
        """
        new_state = self.gol.step(self.ids.grid.visible_width(), self.ids.grid.visible_height())
        self.ids.grid.activated_cells = new_state

    def new_random(self, p: Union[float, int], *args):
        """ Clear the grid and add a random number of living cells

        :param p: If in the range of 0 to 1, select that proportion of cells to make alive.  Otherwise treat as the
        number of cells to make alive.
        :param args: Unused
        :return:
        """
        self.gol.clear()
        self.gol.random(p)

    def dp_stop(self):
        """ Cancel the event that updates the grid.

        :return:
        """
        if self.update_event is not None:
            self.update_event.cancel()
            self.update_event = None

    def dp_start(self):
        """ Start the event that updates the grid

        :return:
        """
        if not self.initialized:
            self.gol.random(self.random_cell_count)
            self.initialized = True
        self.update_event = Clock.schedule_interval(self.gol_update, self.update_rate)


class GameOfLifeApp(App):
    """ For demonstration.

    """

    def build(self):
        panel = GameOfLifePanel()
        panel.dp_start()
        return panel


if __name__ == "__main__":
    GameOfLifeApp().run()
