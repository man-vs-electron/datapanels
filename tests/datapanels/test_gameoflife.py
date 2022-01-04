from datapanels.gameoflife import GameOfLifeEngine


def test_gameoflifeengine():
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