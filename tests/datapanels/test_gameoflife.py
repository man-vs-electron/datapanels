from datapanels.gameoflife import GameOfLifeEngine


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