import random

class Player():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.keys = 0
        self.health = 3
        self.gold = 0
        self.stealth = 0
        self.attackDamage = 1
        self.attackRange = 1
        self.dodgeChance = 0.0
        self.enemies_defeated = 0
        self.direction = 3

    def takeDamage(self, damage):
        if self.dodgeChance < random.random():
            self.health -= damage
        else:
            return False
        return True
    
    def alert(self): #alerts surrounding enemies
        pass

    def movePlayer(self, direction, grid):
        #directions
        dir = None
        if direction == "None":
            return False, False, False, None
        if direction == "left":
            dir = 0
        elif direction == "right":
            dir = 1
        elif direction == "up":
            dir = 2
        elif direction == "down":
            dir = 3

        self.direction = dir

        dx = [-1, 1, 0, 0]
        dy = [0, 0, -1, 1]
        
        move = False
        newFloor = False
        won = False
        tile = grid[self.y + dy[dir]][self.x + dx[dir]] 
        if grid[self.y + dy[dir]][self.x + dx[dir]] == 0: 
            move = True
        elif grid[self.y + dy[dir]][self.x + dx[dir]] == 5:
            move = True
            self.keys += 1
        elif grid[self.y + dy[dir]][self.x + dx[dir]] == 3 and self.keys > 0:
            self.keys -= 1
            move = True
        elif grid[self.y + dy[dir]][self.x + dx[dir]] == 7:
            move = True
            self.gold += 1
        elif grid[self.y + dy[dir]][self.x + dx[dir]] == 6:
            move = True
            newFloor = True
        elif grid[self.y + dy[dir]][self.x + dx[dir]] == 8: #final tile, win the game
            move = True
            won = True
        if move:
            grid[self.y][self.x] = 0
            self.x += dx[dir]
            self.y += dy[dir]
            grid[self.y][self.x] = 2
        if newFloor: #return format: newFloor, won, move_succesful, tile_type
            return True, False, move, tile
        if won:
            return False, True, move, tile
        return False, False, move, tile