import unittest
from game import GameOfLife, GameSettings, GameState


class GameLogicTestCase(unittest.TestCase):
    def setUp(self):
        self.game = GameOfLife(settings=self.__getSettings())
    
    #def tearDown(self):
        # undo changes made during testing (if necessary)
    
    """ Test game init state """
    def test_init(self):
        game_state = self.game._GameOfLife__state
        settings = self.__getSettings()
        assert isinstance(game_state.grid, list) == True
        assert len(game_state.grid) == settings.grid_size[1]
        for row in game_state.grid:
            assert isinstance(row, list) == True
            assert len(row) == settings.grid_size[0]
            for cell in row:
                assert cell == 0
    
    def test_getACCPNeighborsCount(self):
        self.__setManualGrid()
        neighbors_count = [
            [1,3,2,1,0,0,0,0,0,1],
            [4,4,2,1,0,1,1,1,0,2],
            [2,3,3,1,0,1,1,3,2,2],
            [2,2,1,0,0,2,4,4,2,2],
            [0,0,0,0,0,1,2,3,3,1],
            [1,1,0,0,0,1,2,2,1,1],
        ]
        grid_size = (10, 6)
        for y in range(grid_size[1]):
            for x in range(grid_size[0]):
                assert self.game._GameOfLife__getACCPNeighborsCount(x,y) == neighbors_count[y][x]
        
        neighbors_count = [
            [0,1,1,1,1,3,3,2,1,0],
            [0,0,0,0,1,2,4,4,2,0],
            [1,2,2,1,1,2,3,1,1,0],
            [3,3,2,1,0,0,1,1,1,1],
            [2,4,4,2,0,0,0,0,0,1],
            [2,3,1,1,0,1,2,2,1,1],
        ]
        self.game._GameOfLife__state.cur_player_index = 1
        for y in range(grid_size[1]):
            for x in range(grid_size[0]):
                assert self.game._GameOfLife__getACCPNeighborsCount(x,y) == neighbors_count[y][x]
    
    def test_getCellNewStatus(self):
        self.__setManualGrid()
        grid_size = (10, 6)
        grid_next_state = [
            [0,1,0,0,0,0,2,2,0,0],
            [0,0,1,0,0,2,2,0,0,0],
            [1,1,1,0,0,0,0,1,0,0],
            [0,2,2,0,0,0,0,0,1,0],
            [2,2,0,0,0,0,1,1,1,0],
            [0,0,2,0,0,0,0,0,0,0],
        ]
        for y in range(grid_size[1]):
            for x in range(grid_size[0]):
                assert self.game._GameOfLife__getCellNewStatus(x, y) == grid_next_state[y][x]
        
        grid_next_state = [
            [0,1,0,0,0,2,2,2,0,0],
            [0,0,1,0,0,2,2,2,0,0],
            [1,1,1,0,0,0,0,1,0,0],
            [2,2,2,0,0,0,0,0,1,0],
            [2,0,0,0,0,0,1,1,1,0],
            [0,2,0,0,0,0,0,0,0,0],
        ]
        self.game._GameOfLife__playerMove()
        self.game._GameOfLife__state.cur_player_index = 1
        for y in range(grid_size[1]):
            for x in range(grid_size[0]):
                assert self.game._GameOfLife__getCellNewStatus(x, y) == grid_next_state[y][x]
    
    """ Manual test, usually to check if grid calculations for testing are correct
    def test_Manual(self):
        self.__setManualGrid
        self.game._GameOfLife__state.grid = self.__getMove1Grid()

        grid_size = (10, 6)
        grid_next_state = [
            [0,0,0,0,0,2,2,2,0,0],
            [1,0,1,0,0,2,2,2,0,0],
            [0,1,1,0,0,0,0,0,0,0],
            [2,1,2,0,0,0,1,0,1,1],
            [2,0,0,0,0,0,0,1,1,0],
            [0,2,0,0,0,0,0,1,0,0]
        ]
        for y in range(grid_size[1]):
            for x in range(grid_size[0]):
                cell = self.game._GameOfLife__getCellNewStatus(x, y)
                print('x={}, y={}, exp={}, got={}'.format(x, y, grid_next_state[y][x], cell))
                assert cell == grid_next_state[y][x]
        
        grid_next_state = [
            [0,0,0,0,0,2,0,2,0,0],
            [1,0,1,0,0,2,0,2,0,0],
            [0,1,1,0,0,0,2,0,0,0],
            [0,2,0,0,0,0,1,0,1,1],
            [2,0,0,0,0,0,0,1,1,0],
            [0,0,0,0,0,0,2,1,0,0]
        ]
        self.game._GameOfLife__playerMove()
        self.game._GameOfLife__state.cur_player_index = 1
        for y in range(grid_size[1]):
            for x in range(grid_size[0]):
                cell = self.game._GameOfLife__getCellNewStatus(x, y)
                print('x={}, y={}, exp={}, got={}'.format(x, y, grid_next_state[y][x], cell))
                assert cell == grid_next_state[y][x]
    """

    
    def test_AddCell(self):
        self.__setManualGrid()
        assert self.game.AddCell(0, 0, 1) == False
        self.game._GameOfLife__state.phase = 0
        self.game._GameOfLife__state.cur_player_added_cells = 0
        grid = self.game._GameOfLife__state.grid
        
        assert self.game.AddCell(0, 0, 1) == False
        assert self.game.AddCell(1, 0, 1) == True
        assert self.game._GameOfLife__state.grid[0][1] == 1
        assert self.game.AddCell(2, 0, 1) == True
        assert self.game.AddCell(3, 0, 1) == True
        assert self.game.AddCell(4, 0, 1) == True
        assert self.game.AddCell(5, 0, 1) == True

        assert self.game._GameOfLife__state.cur_player_index == 1
        assert self.game._GameOfLife__state.cur_player_added_cells == 0
        grid[0] = [1,1,1,1,1,1,2,2,0,0]
        assert self.game._GameOfLife__state.grid == grid

        assert self.game.AddCell(4, 0, 2) == False
        assert self.game.AddCell(9, 5, 1) == False
        assert self.game.AddCell(9, 5, 2) == True
        assert self.game.AddCell(8, 5, 2) == True
        assert self.game.AddCell(7, 5, 2) == True
        assert self.game.AddCell(6, 5, 2) == True
        assert self.game.AddCell(5, 5, 2) == True

        assert self.game._GameOfLife__state.cur_player_index == 2
        assert self.game._GameOfLife__state.cur_player_added_cells == 5
        assert self.game._GameOfLife__state.phase == 1
        grid[5] = [0,0,2,0,0,2,2,2,2,2]
        assert self.game._GameOfLife__state.grid == grid

    
    def test_GameProcess(self):
        self.__setManualGrid()

        """ First gen move """
        self.game.Move()
        grid = [
            [0,1,0,0,0,2,2,2,0,0],
            [0,0,1,0,0,2,2,2,0,0],
            [1,1,1,0,0,0,0,1,0,0],
            [2,2,2,0,0,0,0,0,1,0],
            [2,0,0,0,0,0,1,1,1,0],
            [0,2,0,0,0,0,0,0,0,0],
        ]
        assert self.game._GameOfLife__state.grid == grid
        assert self.game._GameOfLife__state.cur_player_index == 2
        assert self.game._GameOfLife__state.phase == 1

        """ Second gen move """
        self.game.Move()
        grid = [
            [0,0,0,0,0,2,0,2,0,0],
            [1,0,1,0,0,2,0,2,0,0],
            [0,1,1,0,0,0,2,0,0,0],
            [0,2,0,0,0,0,1,0,1,1],
            [2,0,0,0,0,0,0,1,1,0],
            [0,0,0,0,0,0,2,1,0,0]
        ]
        assert self.game._GameOfLife__state.grid == grid
        assert self.game._GameOfLife__state.cur_player_index == 0
        assert self.game._GameOfLife__state.phase == 0
        assert self.game._GameOfLife__state.cur_round == 2
        assert self.game._GameOfLife__state.cur_round_generation == 1
        assert self.game.Winner == [1]

        """ Adding cells """
        self.game.Move()
        assert self.game._GameOfLife__state.grid == grid
        self.game._GameOfLife__state.players_turn_queue = [1, 2]
        self.game.AddCell(1, 4, 1)
        self.game.AddCell(2, 3, 1)
        self.game.AddCell(2, 4, 1)
        self.game.AddCell(2, 5, 1)
        self.game.AddCell(3, 3, 1)
        assert self.game._GameOfLife__state.cur_player_index == 1
        assert self.game._GameOfLife__state.cur_player_added_cells == 0
        self.game.AddCell(4, 4, 2)
        self.game.AddCell(5, 3, 2)
        self.game.AddCell(5, 4, 2)
        self.game.AddCell(5, 5, 2)
        self.game.AddCell(6, 4, 2)
        assert self.game._GameOfLife__state.cur_player_index == 2
        assert self.game._GameOfLife__state.cur_player_added_cells == 5

        """ Second round """
        self.game.Move()
        self.game.Move()
        assert self.game._GameOfLife__state.cur_round == 3
        assert self.game._GameOfLife__state.phase == -1
        assert self.game.Winner == [1]
    
    
    def __getSettings(self):
        settings = GameSettings(rounds_number=2,
                                new_cells_per_round=5,
                                generations_per_round=2)
        settings.grid_size = (10, 6)
        return settings
    
    def __setManualGrid(self):
        self.game._GameOfLife__state.grid = [
            [1,0,0,0,0,0,2,2,0,0],
            [0,1,1,0,0,2,2,0,0,0],
            [1,1,0,0,0,0,1,2,0,0],
            [0,2,2,0,0,0,0,1,1,0],
            [2,2,0,0,0,0,1,1,0,0],
            [0,0,2,0,0,0,0,0,0,0],
        ]
        self.game._GameOfLife__state.players_turn_queue = [1, 2]
        self.game._GameOfLife__state.cur_player_index = 0
        self.game._GameOfLife__state.phase = 1
        self.grid_size = (10, 6)
    
    def __getStartGrid(self):
        return [
            [1,0,0,0,0,0,2,2,0,0],
            [0,1,1,0,0,2,2,0,0,0],
            [1,1,0,0,0,0,1,2,0,0],
            [0,2,2,0,0,0,0,1,1,0],
            [2,2,0,0,0,0,1,1,0,0],
            [0,0,2,0,0,0,0,0,0,0],
        ]
    
    def __getMove1Grid(self):
        return [
            [0,1,0,0,0,2,2,2,0,0],
            [0,0,1,0,0,2,2,2,0,0],
            [1,1,1,0,0,0,0,1,0,0],
            [2,2,2,0,0,0,0,0,1,0],
            [2,0,0,0,0,0,1,1,1,0],
            [0,2,0,0,0,0,0,0,0,0],
        ]


if __name__ == '__main__':
    unittest.main()