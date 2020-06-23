""" Game logic module """
import abc
import json
import logging
import random
import time


""" Common JSONable functionality """
class JSONable(abc.ABC):
    def ToJSON(self):
        obj_dict = {}
        for param in self.__slots__:
            obj_dict[param] = self.__getattribute__(param)
        return json.dumps(obj_dict)


""" Game settings """
class GameSettings(JSONable):
    __slots__ = ('grid_size', 'players_number',
                'rounds_number', 'generations_per_round',
                'new_cells_per_round')

    def __init__(self,
                generations_per_round: int=20,
                rounds_number: int=10,
                new_cells_per_round: int=20):
        self.grid_size = (30,20)
        self.players_number = 2
        self.generations_per_round = generations_per_round
        self.rounds_number = rounds_number
        self.new_cells_per_round = new_cells_per_round
    
    """ Overwrite setter for validation """
    def __setattr__(self, name, val):
        if not name in self.__slots__:
            return
        
        if name == 'grid_size':
            is_valid = self.__validateGridSize(val)
        else:
            try:
                val = int(val)
            except:
                return
            if name == 'players_number':
                is_valid = 1 <= val <= 5
            elif name == 'generations_per_round':
                is_valid = 1 <= val <= 50
            elif name == 'rounds_number':
                is_valid = 1 <= val <= 30
            elif name == 'new_cells_per_round':
                is_valid = 5 <= val <= 30
        
        if is_valid:
            super().__setattr__(name, val)
    
    """ Grid size must be a tuple of 2 ints >= 10 """
    def __validateGridSize(self, grid_size):
        if not (isinstance(grid_size, tuple) and len(grid_size) == 2):
            return False
        
        try:
            x = int(grid_size[0])
            y = int(grid_size[1])
            if x < 10 or y < 10:
                return False
        except:
            return False
        
        return True


""" Game state """
class GameState(JSONable):
    __slots__ = ('grid', 'phase', 'players_turn_queue', 'cur_player_index',
                'cur_round', 'cur_round_generation', 'cur_winner', 'cur_player_added_cells')

    def __init__(self):
        self.grid = []
        self.phase = 0 # -1 = inactive, 0 = add cells, 1 = generations move
        self.players_turn_queue = []
        self.cur_player_index = 0
        self.cur_round = 1
        self.cur_round_generation = 1
        self.cur_winner = []
        self.cur_player_added_cells = 0
    
    """ Overwrite setter for validation """
    def __setattr__(self, name, val):
        if not name in self.__slots__:
            return
        
        if name == 'grid':
            is_valid = self.__validateGrid(val)
        elif name == 'players_turn_queue':
            is_valid = self.__validatePlayersTurnQueue(val)
        elif name == 'cur_winner':
            is_valid = self.__validateCurWinner(val)
        else:
            """ All other params must be int in some range """
            try:
                val = int(val)
            except:
                return
            if name == 'phase':
                is_valid = -1 <= val <= 1
            elif name == 'cur_player_index' or name == 'cur_player_added_cells':
                is_valid = val >= 0
            elif name == 'cur_round' or name == 'cur_round_generation':
                is_valid = val > 0
            else:
                is_valid = False
        
        if is_valid:
            super().__setattr__(name, val)
    
    """ Grid must be a matrix of ints >= 0 """
    def __validateGrid(self, grid):
        if not isinstance(grid, list):
            return False
        
        for row in grid:
            if not isinstance(row, list):
                return False
            for cell in row:
                try:
                    cell = int(cell)
                    if cell < 0:
                        return False
                except:
                    return False
        
        return True
    
    """ Players turn queue must be a list of ints > 0 """
    def __validatePlayersTurnQueue(self, queue):
        if not isinstance(queue, list):
            return False
        
        for p in queue:
            try:
                p = int(p)
                if p <= 0:
                    return False
            except:
                return False
        
        return True
    
    """ Current winner must be a list (empty or of ints >= 0) """
    def __validateCurWinner(self, winner):
        if not isinstance(winner, list):
            return False
        
        for p in winner:
            try:
                p = int(p)
                if p < 0:
                    return False
            except:
                return False
        
        return True


""" Game logic """
class GameOfLife:
    __slots__ = ('__settings', '__state', 'error_message', 'counts')

    def __init__(self,
                settings: GameSettings=None,
                state: GameState=None):
        if isinstance(settings, GameSettings):
            self.__settings = settings
        else :
            self.__settings = GameSettings()
        
        if isinstance(state, GameState):
            self.__state = state
        else:
            self.__state = GameState()
            self.__resetGrid()
            self.__setPlayersQueue()
        
        self.error_message = ''
        self.__setCounts()
    
    """ Game move logic """
    def Move(self) -> bool:
        """ Move only in valid phase """
        if self.__state.phase != 1:
            self.error_message = 'Add cells first, you must'
            return False
        
        """ Each player's cells step to next generation """
        self.__state.cur_player_index = 0
        while self.__state.cur_player_index < len(self.__state.players_turn_queue):
            self.__playerMove()
            self.__state.cur_player_index += 1
        self.__state.cur_round_generation += 1
        self.__setWinner()

        """ Round generations ended - move to next round """
        if self.__state.cur_round_generation > self.__settings.generations_per_round:
            self.__state.cur_round += 1
            self.__state.cur_round_generation = 1
            if self.IsOver:
                self.__state.phase = -1
                return True
            self.__state.phase = 0
            random.shuffle(self.__state.players_turn_queue)
            self.__state.cur_player_index = 0
            self.__state.cur_player_added_cells = 0
        
        return True
    
    """ Handler for adding cell on field """
    def AddCell(self, cell_x: int, cell_y: int, player: int) -> bool:
        """ Can only add cells in appropriate phase """
        if self.__state.phase != 0:
            self.error_message = 'Generations step phase in cannot cells you add'
            return False
        
        """ Only current turn's player can add cells """
        if player != self.__state.players_turn_queue[self.__state.cur_player_index]:
            self.error_message = 'Wait for your turn you must'
            return False
        
        try:
            cell_x = int(cell_x)
            cell_y = int(cell_y)
            self.__state.grid[cell_y][cell_x] += 0
        except:
            self.error_message = 'Incorrect are cell coordinates provided'
            return False
        
        """ Can't replace cells """
        if self.__state.grid[cell_y][cell_x] != 0:
            self.error_message = 'Already life there is in cell you seek'
            return False
        
        self.__state.grid[cell_y][cell_x] = self.__state.players_turn_queue[self.__state.cur_player_index]
        self.__state.cur_player_added_cells += 1
        if self.__state.cur_player_added_cells >= self.__settings.new_cells_per_round:
            self.__state.cur_player_index += 1
            if self.__state.cur_player_index >= len(self.__state.players_turn_queue):
                self.__state.phase = 1
            else:
                self.__state.cur_player_added_cells = 0
        return True
    
    """ What player has to do next """
    def GetNextAction(self, player_num: int) -> str:
        if self.__state.phase == -1:
            return 'game_over'
        if self.__state.phase == 0 and self.__state.players_turn_queue[self.__state.cur_player_index] == player_num:
            return 'add_cell'
        else:
            return 'wait'
    
    """ Check if sent grid (frontend one) is up-to-date """
    def GridIsActual(self, grid):
        if len(grid) != len(self.__state.grid):
            return False
        
        for y in range(len(grid)):
            if len(grid[y]) != len(self.__state.grid[y]):
                return False
            for x in range(len(grid[y])):
                if grid[y][x] != self.__state.grid[y][x]:
                    return False
        
        return True
    

    """ Reset game grid """
    def __resetGrid(self):
        self.__state.grid = []
        for y in range(self.__settings.grid_size[1]):
            self.__state.grid.append([])
            for _ in range(self.__settings.grid_size[0]):
                self.__state.grid[y].append(0)
    
    """ Set players queue """
    def __setPlayersQueue(self):
        self.__state.players_turn_queue = []
        for p in range(self.__settings.players_number):
            self.__state.players_turn_queue.append(p + 1)
        random.shuffle(self.__state.players_turn_queue)
    
    # ACCP = Alive Cell of Current Player
    """ Get count of cell's neighbors that are ACCP """
    def __getACCPNeighborsCount(self, cell_x, cell_y) -> int:
        count = 0
        for y in range(cell_y - 1, cell_y + 2):
            for x in range(cell_x - 1, cell_x + 2):
                if x != cell_x or y != cell_y:
                    cell = self.__state.grid[y % len(self.__state.grid)][x % len(self.__state.grid[0])]
                    if cell == self.__state.players_turn_queue[self.__state.cur_player_index]:
                        count += 1
        return count
    
    """ Get status of cell after current player's move """
    def __getCellNewStatus(self, cell_x, cell_y) -> int:
        c = self.__state.grid[cell_y][cell_x]
        neighbors = self.__getACCPNeighborsCount(cell_x, cell_y)
        """
            if cell is ACCP:
                if it has 2 or 3 ACCP neighbors:
                    * it remains unchanged
                else:
                    * it dies
            else:
                if it has 3 ACCP neighbors:
                    * it becomes ACCP
                else:
                    * it remains unchanged
        """
        if c == self.__state.players_turn_queue[self.__state.cur_player_index]:
            if not 2 <= neighbors <= 3:
                c = 0
        else:
            if neighbors == 3:
                c = self.__state.players_turn_queue[self.__state.cur_player_index]
        return c
    
    """ Process move of current player, update grid accordingly """
    def __playerMove(self):
        grid = []
        for y in range(len(self.__state.grid)):
            grid.append([])
            for x in range(len(self.__state.grid[0])):
                grid[y].append(self.__getCellNewStatus(x, y))
        self.__state.grid = grid
    

    """ Calculate counts of players' alive cells """
    def __setCounts(self):
        self.counts = [0]
        for _ in range(self.__settings.players_number):
            self.counts.append(0)
        for row in self.__state.grid:
            for cell in row:
                if cell > 0:
                    self.counts[cell] += 1
    
    """ Set game current winner """
    def __setWinner(self):
        self.__setCounts()
        self.__state.cur_winner = [0]
        for i in range(1, len(self.counts)):
            if self.counts[i] > self.counts[self.__state.cur_winner[0]]:
                self.__state.cur_winner = [i]
            elif self.counts[i] > 0 and self.counts[i] == self.counts[self.__state.cur_winner[0]]:
                self.__state.cur_winner.append(i)
    
    
    @property
    def IsOver(self) -> bool:
        return self.__state.cur_round > self.__settings.rounds_number
    
    @property
    def Winner(self) -> int:
        return self.__state.cur_winner
    
    @property
    def WinnerMessage(self) -> str:
        if len(self.__state.cur_winner) > 1:
            return 'Tie between players ' + ', '.join(str(p) for p in self.__state.cur_winner)
        
        if len(self.__state.cur_winner) == 1 and self.__state.cur_winner[0] != 0:
            winner_type = 'Winner' if self.__state.phase == -1 else 'Leader'
            return '{}: player {}'.format(winner_type, self.__state.cur_winner[0])
        
        return 'No life present'
    
    @property
    def Status(self) -> str:
        if self.__state.phase == -1:
            return 'Game over. {}'.format(self.WinnerMessage)
        elif self.__state.phase == 1:
            return 'Cell generations proceeding'
        else:
            return 'Player {} adding cells, {} remaining'.format(self.__state.players_turn_queue[self.__state.cur_player_index],
                                                                 self.__settings.new_cells_per_round - self.__state.cur_player_added_cells)