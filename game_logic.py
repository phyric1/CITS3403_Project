import random
from flask import request, jsonify

class DungeonGame():
    '''class representing a game instance and all its properties'''
    #player -> health, attack
    #dificulty
    #floors
    #enemies
    #grid/board (walls and such)
    #cards/deck -> active card effects
    def __init__(self):
        self.grid = Grid()
        self.player = Player(self.grid.startX, self.grid.startY)
        self.turnNum = 0

    def getGridObject(self):
        return self.grid
    
    def getGrid(self):
        return self.grid.grid
    
    def getFakeGrid(self):
        return self.grid.fake_grid
    
    def getPlayer(self):
        return self.player

class Player():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def movePlayer(self, direction, game):
        grid = game.getGrid()
        if direction == "left":
            if grid[self.y][self.x-1] == 0: 
                grid[self.y][self.x] = 0
                self.x -= 1
                grid[self.y][self.x] = 2
        elif direction == "right":
            if grid[self.y][self.x+1] == 0: 
                grid[self.y][self.x] = 0
                self.x += 1
                grid[self.y][self.x] = 2
        elif direction == "up":
            if grid[self.y-1][self.x] == 0: 
                grid[self.y][self.x] = 0
                self.y -= 1
                grid[self.y][self.x] = 2
        elif direction == "down":
            if grid[self.y+1][self.x] == 0: 
                grid[self.y][self.x] = 0
                self.y += 1
                grid[self.y][self.x] = 2

        game.getGridObject().updateVisibility(self)
        return_grid = game.getGridObject().gridProxy()

        return jsonify({"grid": return_grid})

class Grid():
    grid = [[]]
    FOV = 4
    HEIGHT = int
    WIDTH = int
    
    def __init__(self):
        self.grid, self.startX, self.startY = self.generate_dungeon()
        self.isVisible = [[False] * 32 for _ in range(20)]
        self.fake_grid = [[-1] * 32 for _ in range(20)]

    def updateVisibility(self, player: Player):
        for i in range(player.y-2, player.y+3):
            for j in range(player.x-2, player.x+3):
                if 0 <= i < 20 and 0 <= j < 32:
                    self.isVisible[i][j] = True
    
    def gridProxy(self):
        for i in range(0,20):
            for j in range(0,32):
                if self.isVisible[i][j]:
                    self.fake_grid[i][j] = self.grid[i][j]
                else:
                    self.fake_grid[i][j] = -1
        return self.fake_grid

    def generate_dungeon(self):    
        GRID_HEIGHT = 20
        GRID_WIDTH = 32

        #Room constants
        MIN_ROOMS = 3
        MAX_ROOMS = 5
        MAX_WIDTH = 7
        MAX_HEIGHT = 7
        MIN_WIDTH = 7
        MIN_HEIGHT = 7

        grid = [[1] * GRID_WIDTH for _ in range(GRID_HEIGHT)]

        class Room():
            def __init__(self, width, height, x, y,):
                self.x = x
                self.y = y
                self.x2 = x + width -1
                self.y2 = y + height -1

            def center(self):
                centerX = (self.x + (self.x2)) // 2
                centerY = (self.y + (self.y2)) // 2
                return centerX, centerY

        def overlap(room1, room2):
            if room2.x2 < room1.x or room2.x > room1.x2:
                return True
            if room2.y2 < room1.y or room2.y > room1.y2:
                return True
            return False

        def carve_corridor(room1, room2):
            x1, y1 = room1.center()
            x2, y2 = room2.center()
            
            if random.random() < 0.5: #randomise corridor direction
                #horizontal first
                for i in range(min(x1,x2),max(x1,x2)+1):
                    if grid[y1][i] != 0:
                        grid[y1][i] = 0
                for i in range(min(y1,y2),max(y1,y2)+1):
                    if grid[i][x2] != 0:
                        grid[i][x2] = 0
            else:
                for i in range(min(y1,y2),max(y1,y2)+1):
                    if grid[i][x2] != 0:
                        grid[i][x2] = 0
                for i in range(min(x1,x2),max(x1,x2)+1):
                    if grid[y1][i] != 0:
                        grid[y1][i] = 0

        def distance(room1, room2):
            x1, y1 = room1.center()
            x2, y2 = room2.center()
            return (abs(x1-x2) + abs(y1-y2))
        
        rooms = []
        #initialize grid
        success = False
        for i in range(8):
            success = False
            while success == False:
                width = random.randint(3, 5)
                height = random.randint(3, 5)
                x = random.randint(1, GRID_WIDTH - width - 1)
                y = random.randint(1, GRID_HEIGHT - height - 1)
                newRoom = Room(width, height, x, y)

                valid = True
                for r in rooms:
                    if not overlap(newRoom, r):
                        valid = False
                        break
                if valid:
                    if len(rooms) > 0:
                        carve_corridor(newRoom, rooms[-1])
                    rooms.append(newRoom)
                    success = True

        for room in rooms:
            #carve out rooms
            for i in range(room.y, room.y2+1):
                for j in range(room.x, room.x2+1):
                    grid[i][j] = 0

        startRoom = Room
        endRoom = Room
        max_distance = -1
        for room in rooms:
            for r in rooms:
                if distance(room, r) > max_distance:
                    max_distance = distance(room, r)
                    startRoom = room
                    endRoom = r
        startX, startY = startRoom.center()
        endX, endY = endRoom.center()
        grid[startY][startX] = 2
        grid[endY][endX] = 3

        #block off end room
        tempArray = []
        for i in range(endRoom.x, endRoom.x2+1):
            if grid[endRoom.y-1][i] == 0:
                grid[endRoom.y-1][i] = 1
                tempArray.append((endRoom.y-1, i))
        if len(tempArray) > 0:
            y, x = tempArray[random.randint(0, len(tempArray)-1)]
            grid[y][x] = 3
        tempArray.clear()
        for i in range(endRoom.x, endRoom.x2+1):
            if grid[endRoom.y2+1][i] == 0:
                grid[endRoom.y2+1][i] = 1
                tempArray.append((endRoom.y2+1, i))
        if len(tempArray) > 0:
            y, x = tempArray[random.randint(0, len(tempArray)-1)]
            grid[y][x] = 3
        tempArray.clear()
        for i in range(endRoom.y, endRoom.y2+1):
            if grid[i][endRoom.x-1] == 0:
                grid[i][endRoom.x-1] = 1
                tempArray.append((i, endRoom.x-1))
        if len(tempArray) > 0:
            y, x = tempArray[random.randint(0, len(tempArray)-1)]
            grid[y][x] = 3
        tempArray.clear()
        for i in range(endRoom.y, endRoom.y2+1):
            if grid[i][endRoom.x2+1] == 0:
                grid[i][endRoom.x2+1] = 1
                tempArray.append((i, endRoom.x2+1))
        if len(tempArray) > 0:
            y, x = tempArray[random.randint(0, len(tempArray)-1)]
            grid[y][x] = 3

        return grid, startX, startY
    
def shortestPath():
    return None