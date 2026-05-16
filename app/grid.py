import random
from app.player import Player
from collections import deque
from app.enemies import Goblin

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
    
class Grid():
    '''Class that handles all logic to do with the game grid'''
    startRoom = Room
    endRoom = Room
    def __init__(self, WIDTH, HEIGHT, FOV, lastLevel):
        self.HEIGHT = HEIGHT
        self.WIDTH = WIDTH
        self.FOV = FOV
        self.grid, self.roomsList = self.generate_dungeon(lastLevel)
        self.isVisible = [[False] * self.WIDTH for _ in range(self.HEIGHT)]
        self.fake_grid = [[-1] * self.WIDTH for _ in range(self.HEIGHT)]

    def spawnEnemies(self, enemyCount):
        enemyList = []
        for i in range(enemyCount):
            enemySpawn = self.roomsList[random.randint(0, len(self.roomsList)-1)]
            enemyX, enemyY = enemySpawn.center()
            self.roomsList.remove(enemySpawn)

            self.grid[enemyY][enemyX] = 4
            enemyList.append(Goblin(enemyX, enemyY))
        return enemyList

    def spawnGold(self, goldCount):
        for i in range(goldCount):
            success = False
            while success == False:
                x = random.randint(0, self.WIDTH -1 )
                y = random.randint(0, self.HEIGHT - 1)
                if self.grid[y][x] == 0:
                    self.grid[y][x] = 7
                    success = True

    def distance_map(self, player: Player):
        '''Returns distance map from player to all tiles, used for enemy pathfinding'''
        dist_map = [[-1] * self.WIDTH for _ in range(self.HEIGHT)]

        queue = deque()
        x, y = player.x, player.y

        queue.append((x, y))
        dist_map[y][x] = 0

        while queue:
            x, y = queue.popleft()
            dx = [-1, 0, 0, 1]
            dy = [0, -1, 1, 0]
            for i in range(4):
                zx, zy = x + dx[i], y + dy[i]
                if not (0 <= zx < self.WIDTH and 0 <= zy < self.HEIGHT):
                    continue
                if self.grid[zy][zx] == 0 and dist_map[zy][zx] == -1:
                    dist_map[zy][zx] = dist_map[y][x] + 1
                    queue.append((zx, zy))
        return dist_map

    def updateVisibility(self, player: Player): #updates visible tiles
        for i in range(player.y-4, player.y+5):
            for j in range(player.x-4, player.x+5):
                if 0 <= i < 20 and 0 <= j < 33:
                    self.isVisible[i][j] = True
    
    def gridProxy(self): #returns proxy grid with limited FOV
        for i in range(self.HEIGHT):
            for j in range(self.WIDTH):
                if self.isVisible[i][j]:
                    self.fake_grid[i][j] = self.grid[i][j]
                else:
                    self.fake_grid[i][j] = -1
        return self.fake_grid

    def generate_dungeon(self, lastLevel):    
        #Room constants
        ROOM_COUNT = 8
        MIN_WIDTH = 4
        MIN_HEIGHT = 4
        MAX_WIDTH = 7
        MAX_HEIGHT = 7

        grid = [[1] * self.WIDTH for _ in range(self.HEIGHT)]

        def overlap(room1, room2):
            #returns true if rooms overlap
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
            #returns manhattan distance between 2 rooms
            x1, y1 = room1.center()
            x2, y2 = room2.center()
            return (abs(x1-x2) + abs(y1-y2))
        
        rooms = []
        #initialize grid
        success = False
        for i in range(ROOM_COUNT):
            success = False
            while success == False:
                width = random.randint(MIN_WIDTH, MAX_WIDTH)
                height = random.randint(MIN_HEIGHT, MAX_HEIGHT)
                x = random.randint(1, self.WIDTH - width - 1)
                y = random.randint(1, self.HEIGHT - height - 1)
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
        if lastLevel:
            grid[endY][endX] = 8
        else:
            grid[endY][endX] = 6

        rooms.remove(startRoom)
        self.startRoom = startRoom
        rooms.remove(endRoom)
        self.endRoom = endRoom

        keyRoom = rooms[random.randint(0, len(rooms)-1)]
        KeyX, KeyY = keyRoom.center()
        grid[KeyY][KeyX] = 5
        rooms.remove(keyRoom)

        #block off end room
        #fix block room bug where door isnt connected to end room
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
        return grid, rooms