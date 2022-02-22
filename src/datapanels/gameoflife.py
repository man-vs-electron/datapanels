""" DataPanels implementation of Conway's Game of Life

See https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life for details about
the game.

"""
import random
from typing import Tuple, Set, Optional, Union, List
import re
import numpy as np
from kivy.lang.builder import Builder
from kivy.properties import ListProperty, NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
from kivy.app import App
from kwidgets.uix.pixelatedgrid import PixelatedGrid


def translate(state: Set[Tuple[int, int]], x: int, y: int, additive: bool=False) -> Set[Tuple[int, int]]:
    """ Move the object the specified number of x and y values

    :param state: original state
    :param x: horizontal distance to move the object
    :param y: vertical distance to move the object
    :return: new, translated state
    """
    return set([(t[0]+x, t[1]+y) for t in state]).union(state if additive else set())


def horizontal_flip(state: Set[Tuple[int, int]], additive: bool=False) -> Set[Tuple[int, int]]:
    """ Flip the object horizontally around the center

    :param state: original state
    :return: new modified state
    """
    max_x = max([t[0] for t in state])
    min_x = min([t[0] for t in state])
    x_width = max_x-min_x

    return set([( x_width-t[0]+2*min_x, t[1] ) for t in state]).union(state if additive else set())


def vertical_flip(state: Set[Tuple[int, int]], additive: bool=False) -> Set[Tuple[int, int]]:
    """ Flip the object vertically around the center

    :param state: original state
    :return: new modified state
    """
    max_y = max([t[1] for t in state])
    min_y = min([t[1] for t in state])
    y_width = max_y-min_y

    return set([( t[0], y_width-t[1]+2*min_y ) for t in state]).union(state if additive else set())


def rotate_90(state: Set[Tuple[int, int]], origin: Tuple[int, int], additive: bool=False) -> Set[Tuple[int, int]]:
    """ Rotate the object 90 degrees to the left with respect to the provide origin

    :param state: original state
    :param origin: The point of the rotation
    :return: new modified state
    """
    return set([( origin[1]-t[1]+origin[0], t[0]-origin[0]+origin[1]) for t in state]).union(state if additive else set())


def multi_transform(state: Set[Tuple[int, int]], ops: List[Union[str, Tuple[str, int], Tuple[str, Tuple[int, int]]]], additive_final: bool=False) -> Set[Tuple[int, int]]:
    ans = set(state)
    for op in ops:
        if isinstance(op, tuple):
            if op[0].upper() == "T":
                ans = translate(ans, op[1], False)
            if op[0].upper() == "R":
                ans = rotate_90(ans, op[1], False)
            else:
                raise RuntimeError("Invalid syntax. Ops must be a list where each member is in the form (T, dist)|(R, (x,y)|H|V")
        elif op.upper() == 'H':
            ans = horizontal_flip(ans, False)
        elif op.upper() == 'V':
            ans = vertical_flip(ans, False)
        else:
            raise RuntimeError("Invalid syntax. Ops must be a list where each member is in the form (T, dist)|(R, (x,y)|H|V")
    return ans.union(state if additive_final else set())


def rle_decode(rle_text: str) -> Set[Tuple[int, int]]:
    """
    Adapted from: https://github.com/Robert-Phan/python-conway/blob/master/main.py
    :param rle_text:
    :return:
    """
    ans = []
    x=0
    y=0
    for g in re.findall(r"\d*b|\d*o|\d*\$", rle_text):
        num = 1 if len(g)==1 else int(g[:-1])
        code = g[-1]
        if code=="$":
            y += num
            x = 0
        if code=="b":
            x += num
        if code=="o":
            for j in range(0,num):
                ans.append((x,y))
                x += 1
    return set(ans)

# Patterns taken from LifeWiki: https://conwaylife.com/wiki/Main_Page

basic_patterns = {
    "glider": rle_decode("bob$2bo$3o!"),
    "canada goose": rle_decode("3o10b$o9b2ob$bo6b3obo$3b2o2b2o4b$4bo8b$8bo4b$4b2o3bo3b$3bobob2o4b$3bobo2bob2ob$2bo4b2o4b$2b2o9b$2b2o!"),
    "Copperhead": rle_decode("b2o2b2o$3b2o$3b2o$obo2bobo$o6bo2$o6bo$b2o2b2o$2b4o2$3b2o$3b2o!"),
    "Coe Ship": rle_decode("4b6o$2b2o5bo$2obo5bo$4bo3bob$6bo3b$6b2o2b$5b4ob$5b2ob2o$7b2o!")
}


initial_patterns = {
    "R-pentomino": ((1, 0), (0, 1), (1, 1), (1, 2), (2, 2)),
    "Merzenich's p31": rle_decode("7b2obo2bob2o7b$2o4bo2bo4bo2bo4b2o$2o5bobo4bobo5b2o$8bo6bo8b6$8bo6bo8b$2o5bobo4bobo5b2o$2o4bo2bo4bo2bo4b2o$7b2obo2bob2o!"),
    "68P16": rle_decode("10b2o3b2o$10b2o3b2o$6bo$2o3b2o$2o2bo10bo$5bo3b2o2b2obo$5bo3bo6b2o2$2o$2o3bo7b2o$5b2o7bo3b2o$18b2o2$2b2o6bo3bo$3bob2o2b2o3bo$4bo10bo2b2o$13b2o3b2o$13bo$3b2o3b2o$3b2o3b2o!"),
    "65P48": rle_decode("""6bo3b2o$7b2ob2o$5bobo$6bo$2o2b3o5bobo2bo$2o9bob5o2$10bob4o$10bo5bo$11b2o2b2o$9bobobo3b2o$8bobo2b3o3bo$8bo2b2o4b2obo$7b2o4b3o3bo$13bo2b3o$16bo!"""),
    "Traffic Circle": rle_decode("""21b2o4b2o19b$21bobo2bobo19b$23bo2bo21b$22b2o2b2o20b$21b3o2b3o19b$23bo
2bo21b$31bo16b$30bob2o14b$34bo13b$26bo3bo2bobo12b$26bo5bo2bo12b$26bo6b
2o13b$9b2o37b$8bo2bo10b3o3b3o17b$7bobobo36b$6b3obo15bo21b$6b3o17bo21b$
26bo21b$12b3o33b$2o2bo16b3o24b$o2b2o5bo5bo31b$b5o4bo5bo2bo5bo17bo2b2o$
10bo5bo2bo5bo17b2o2bo$19bo5bo7b3o6b5ob$b5o6b3o33b$o2b2o16b3o7bo5bo10b$
2o2bo26bo5bo4b5ob$31bo5bo5b2o2bo$43bo2b2o$33b3o12b$39b2o7b$38b3o7b$37b
ob2o7b$36bobo9b$20b3o13bo2bo8b$37b2o9b$13b2o4bo2bo25b$12bo2bo32b$12bob
obo31b$13bo2bo31b$17bo30b$14bobo31b$21bo2bo23b$19b3o2b3o21b$20b2o2b2o
22b$21bo2bo23b$19bobo2bobo21b$19b2o4b2o!"""),
    "Space Ship (160P10H2V0)": rle_decode("""7bobobo7b$6b7o6b$5bo7bo5b$b3ob3o3b3ob3ob$o17bo$bo7bo7bob$bob2o9b2obob
2$2b3o9b3o2b$2b3o9b3o2b$5bo7bo5b$bo4bo5bo4bob$bobo11bobob$7bo3bo7b$7bo
3bo7b$5bo2bobo2bo5b$5bo7bo5b$4bo9bo4b$4bobo5bobo4b$4b2obo3bob2o4b$5bob
2ob2obo5b$7bobobo7b$8bobo8b$6bobobobo6b$5b2obobob2o5b$8bobo8b$7b2ob2o
7b$4b3obobob3o4b$4bobobobobobo4b$4bo3bobo3bo4b$8bobo8b$4bo2b5o2bo4b$3b
4o5b4o3b$b2o13b2ob$b2obo9bob2ob$2bobo4bo4bobo2b$4b2o7b2o!"""),
    "Space Ship (Barge 2)": rle_decode("""14b3ob3o14b$13bo2bobo2bo13b$12bo3bobo3bo12b$7b3obo2bobobobo2bob3o7b$6b
o2bobo4bobo4bobo2bo6b$5bo3bobobobo3bobobobo3bo5b$5bo23bo5b$7bo19bo7b$
4bobo21bobo4b$3b2obob3o13b3obob2o3b$2bobobo3bo13bo3bobobo2b$b2obo25bob
2ob$o3bo5b2o11b2o5bo3bo2$2ob2o25b2ob2o!"""),
}


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
        Button:
            text: 'Random Ship'
            on_press: root.random_small()
        Button:
            id: menu_btn
            text: 'Patterns'
            on_release: root.choose_patterns()
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
    pattern_dropdown: ObjectProperty(None)
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
        self.pattern_dropdown = DropDown()
        for t in initial_patterns.keys():
            b = Button(text=t)
            b.size_hint_y = None
            b.height = 44
            b.bind(on_release = lambda btn: self.set_pattern(btn.text))
            self.pattern_dropdown.add_widget(b)

    def choose_patterns(self, *args):
        self.pattern_dropdown.open(self.ids.menu_btn)

    def random_small(self):
        k = np.random.choice(list(basic_patterns.keys()))
        pattern = basic_patterns[k]
        for _ in range(0,np.random.randint(0, 4)):
            pattern = rotate_90(pattern, (0,0))
        xt = np.random.randint(0, self.ids.grid.visible_width())
        yt = np.random.randint(0, self.ids.grid.visible_height())
        self.gol.active_cells = self.gol.active_cells.union(translate(pattern, xt, yt))



    def set_pattern(self, pattern_name):
        self.pattern_dropdown.select(None)
        self.gol.clear()
        pattern = initial_patterns[pattern_name]
        pattern_xt = int((self.ids.grid.visible_width()/2)-(max([p[0] for p in pattern])-min([p[0] for p in pattern]))/2)
        pattern_yt = int((self.ids.grid.visible_height()/2)-(max([p[1] for p in pattern])-min([p[1] for p in pattern]))/2)
        self.gol.active_cells = translate(initial_patterns[pattern_name], pattern_xt, pattern_yt)


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
        #panel = GameOfLifePanel()
        panel = Builder.load_string("""
GameOfLifePanel:
    cell_length: 5        
""")
        panel.dp_start()
        return panel


if __name__ == "__main__":
    GameOfLifeApp().run()
