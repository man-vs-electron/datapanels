from datapanels.gameoflife import GameOfLifeEngine, vertical_flip, horizontal_flip, translate, rotate_90


def test_gameoflifeengine_step():
    gol = GameOfLifeEngine()
    gol.active_cells = {(0, 1), (1, 1), (2, 1)}
    gol.step(2, 2)
    assert gol.active_cells == {(1, 0), (1, 1), (1, 2)}
    gol.step(2, 2)
    assert gol.active_cells == {(0, 1), (1, 1), (2, 1)}

    gol = GameOfLifeEngine()
    gol.active_cells = {(1,1)}
    gol.step(2, 2)
    assert gol.active_cells == set()

    gol = GameOfLifeEngine()
    gol.active_cells = {(0, 1), (1, 1), (2, 1)}
    gol.step(2, 1)
    assert gol.active_cells == {(1, 0), (1,1)}
    gol.step(2, 1)
    assert gol.active_cells == set()


def test_gameoflifeengine_clear():
    gol = GameOfLifeEngine()
    gol.active_cells = {(0, 1), (1, 1), (2, 1)}
    gol.clear()
    assert len(gol.active_cells) == 0


def test_gameoflifeengine_clear():
    gol = GameOfLifeEngine()
    gol.random(10)
    assert len(gol.active_cells) >0

    gol = GameOfLifeEngine()
    gol.random(.5)
    assert len(gol.active_cells) >0


def test_translate():
    assert translate({(2,2), (3, 3), (4, 4)}, 1, 2) == {(3, 4), (4, 5), (5, 6)}


def test_horizontal_flip():
    assert horizontal_flip({(2,2), (3, 3), (4, 4)}) == {(2, 4), (3, 3), (4, 2)}
    assert horizontal_flip({(4,4), (5,4), (4,5), (5,5)}) == {(4,4), (5,4), (4,5), (5,5)}
    assert horizontal_flip({(3,3), (4,3), (5, 6), (6,3)}) == {(3,3), (4,6), (5, 3), (6,3)}


def test_vertical_flip():
    assert vertical_flip({(2, 2), (3, 3), (4, 4)}) == {(2, 4), (3, 3), (4, 2)}
    assert vertical_flip({(4, 4), (5, 4), (4, 5), (5, 5)}) == {(4, 4), (5, 4), (4, 5), (5, 5)}
    assert vertical_flip({(3, 3), (4, 3), (5, 6), (6, 3)}) == {(3, 6), (4, 6), (5, 3), (6, 6)}


def test_rotate_90():
    assert rotate_90({(0,0), (1,0), (2,0)}, (0,0)) == {(0,0), (0,1), (0,2)}
    assert rotate_90({(5,0), (6,0), (7,0)}, (5,0)) == {(5,0), (5,1), (5,2)}
    assert rotate_90({(5,0), (6,0), (7,0)}, (0,0)) == {(0,5), (0,6), (0,7)}
    assert rotate_90({(0,0), (1,1), (2,2)}, (0, 0)) == {(0,0), (-1,1), (-2,2)}
    assert rotate_90(rotate_90(rotate_90(rotate_90({(0,0), (1,1), (2,2)}, (0, 0)), (0,0)), (0,0)), (0,0)) == {(0,0), (1,1), (2,2)}

