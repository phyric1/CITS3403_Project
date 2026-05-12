import random
from flask import request, jsonify
from entities import Enemy, Gold, Goblin
from cards_logic import PlayerDeck
import cards_logic
from collections import deque
from app.utils import get_user_deck

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
            
class DungeonGame():
    '''class representing a game instance and all its properties'''
    #dificulty
    #floors

    def __init__(self):
        #used to start game
        self.level = 0
        self.dificulty = "Easy"
        self.player = Player(0, 0)
        self.generate_floor()
        self.turnNum = 0
        self.isVisible = False
        self.filter = [[0] * 32 for _ in range(20)]
        self.playerDeck: PlayerDeck
        self.hand = []
        self.timeStopped = False
        self.tailwind = 0

    def cardProcessor(self, card):
        #check if card type matches active master cards
        match card.card.name:
            case "Tailwind":
                self.tailwind = 3
            case "Teleport":
                success = False
                while success == False:
                    x = random.randint(0, 31)
                    y = random.randint(0, 19)
                    if self.grid.grid[y][x] == 0:
                        self.grid.grid[self.player.y][self.player.x] = 0
                        self.player.x, self.player.y = x, y
                        self.grid.grid[y][x] = 2
                        success = True
            case "Acrobatics":
                pass
            case "Sprint":
                pass
            case "Timestop":
                self.timeStopped = True
            case "Rest":
                self.player.health += 1
            case "Heal":
                self.player.health += 2
            case "Guard":
                self.player.dodgeChance += 0.02
            case "Parry":
                self.player.dodgeChance += 0.05
            case "Strength":
                self.player.attackDamage += 1
            case "Dexterity":
                self.player.attackDamage += 1
            case "Dagger":
                x = self.player.x
                y = self.player.y
                dx = [-1, 1, 0, 0]
                dy = [0, 0, -1, 1]
                for dir in range(4):
                    #if self.grid.grid[y + dy[dir]][x + dx[dir]] == 4: 
                        self.filter[y + dy[dir]][x + dx[dir]] = 5
            case "Dash Attack":
                self.player.attackDamage += 1
            case "Meteor":
                self.player.attackDamage += 1
            case "Bear Trap":
                self.player.attackDamage += 1
            case "Silence Falls":
                self.player.stealth += 1
            case "Shadow Sneak":
                self.player.stealth += 2
            case "Dynamite":
                grid = self.grid.grid
                radius = 2
                x  = self.player.x
                y  = self.player.y
                for i in range(y - radius, y + radius + 1):
                    for j in range(x - radius, x + radius + 1):
                        if grid[i][j] == 1:
                            grid[i][j] = 0
            case "Eye for Treasure":
                self.grid.spawnGold(1)
            case "Light the Way":
                self.isVisible = True
            case "Key to Victory":
                self.player.keys += 1
            case "Recycle":
                self.playerDeck.deck.append(self.playerDeck.discard[0])
                self.playerDeck.deckSize = len(self.playerDeck.deck)
        return card

    def generate_floor(self): #generates a new dungeon floor
        self.grid = Grid()
        x, y = self.grid.startRoom.center()
        self.player.x = x
        self.player.y = y
        self.enemies = []
        self.enemies = self.grid.spawnEnemies()
        self.grid.spawnGold(2)
        self.level += 1

    def advance_game(self, input):
        '''advances the game by one turn'''
        self.filter = [[0] * 32 for _ in range(20)]
        grid = self.getGrid()
        discard_data = None

        newFloor = False
        if input in ["left", "right", "up", "down"]:
            newFloor = self.player.movePlayer(input, grid)  #move player
        elif input in ["0", "1", "2"] and self.tailwind == 0:
            if self.hand:
                card = self.cardProcessor(self.playerDeck.useSlot(int(input)))
                discard_data = self.playerDeck.serialize_card(card)
                #all cards flip over
                #card is already sent to discard slot
                #load new grid data
                #activate new event listeners
                #upon new input, increment turn and continue advancing the game

        if self.tailwind > 0:
            self.tailwind -= 1
            self.getGridObject().updateVisibility(self.player)
            if self.isVisible:
                return_grid = self.grid.grid
            else:
                return_grid = self.getGridObject().gridProxy()
            self.turnNum += 1 #increment turn count unless card effect overrides it
            return jsonify({
                "grid": return_grid,
                "filter": self.filter,
                "turn": self.turnNum,
                "hp": self.player.health,
                "keys": self.player.keys,
                "gold": self.player.gold,
                "gold": self.player.gold,
                "stealth": self.player.stealth,
                "floor": self.level,
                "deckMax": self.playerDeck.deckMax,
                "deckSize": self.playerDeck.deckSize,
            })

    #start of phase 2
        #draw new cards
        self.playerDeck.hand = self.playerDeck.shuffle(self.playerDeck.deck) #move logic to cards file
        card_data = [self.playerDeck.serialize_card(card) for card in self.playerDeck.hand]

        if newFloor:
            self.timeStopped = False
            self.generate_floor()
            self.getGridObject().updateVisibility(self.player)
            if self.isVisible:
                return_grid = self.grid.grid
            else:
                return_grid = self.getGridObject().gridProxy()
            self.turnNum += 1
            return jsonify({
                "grid": return_grid,
                "filter": self.filter,
                "turn": self.turnNum,
                "hp": self.player.health,
                "keys": self.player.keys,
                "gold": self.player.gold,
                "stealth": self.player.stealth,
                "floor": self.level,
                "cards": card_data,
                "deckMax": self.playerDeck.deckMax,
                "deckSize": self.playerDeck.deckSize,
            })
        if not self.timeStopped:
            for enemy in self.enemies: #move enemies
                enemy.moveEnemy(grid, self.grid.distance_map(self.player), self.filter)
                enemy.attack(self.player)
        #apply any map interactions
        #apply any card passive card effects

        self.getGridObject().updateVisibility(self.player)
        if self.isVisible:
            return_grid = self.grid.grid
        else:
            return_grid = self.getGridObject().gridProxy()
        self.turnNum += 1 #increment turn count unless card effect overrides it
        return jsonify({
            "grid": return_grid,
            "filter": self.filter,
            "turn": self.turnNum,
            "hp": self.player.health,
            "keys": self.player.keys,
            "gold": self.player.gold,
            "gold": self.player.gold,
            "stealth": self.player.stealth,
            "floor": self.level,
            "cards": card_data,
            "discard": discard_data,
            "deckMax": self.playerDeck.deckMax,
            "deckSize": self.playerDeck.deckSize,
        })

    def getGridObject(self): #return grid object
        return self.grid
    
    def getGrid(self):  #return grid as 2d array
        return self.grid.grid
    
    def getFakeGrid(self): #return grid with limited FOV
        return self.grid.fake_grid
    
    def getPlayer(self): #return player object
        return self.player

class Player():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.keys = 0
        self.health = 3
        self.gold = 0
        self.stealth = 0
        self.attackDamage = 1
        self.dodgeChance = 0.0

    def takeDamage(self, damage):
        if self.dodgeChance < random.random():
            self.health -= damage
        else:
            print("dodge")
        return self.health
    
    def attack(self, damage):
        pass

    def alert(self):
        pass
    
    def movePlayer(self, direction, grid):
        #directions
        dir = None
        if direction == "None":
            return
        if direction == "left":
            dir = 0
        elif direction == "right":
            dir = 1
        elif direction == "up":
            dir = 2
        elif direction == "down":
            dir = 3

        dx = [-1, 1, 0, 0]
        dy = [0, 0, -1, 1]
        
        if grid[self.y + dy[dir]][self.x + dx[dir]] == 0: 
            grid[self.y][self.x] = 0
            self.x += dx[dir]
            self.y += dy[dir]
            grid[self.y][self.x] = 2
        elif grid[self.y + dy[dir]][self.x + dx[dir]] == 5:
            #move this to collision function eventually
            #pickup keys
            grid[self.y][self.x] = 0
            self.x += dx[dir]
            self.y += dy[dir]
            grid[self.y][self.x] = 2
            self.keys += 1
        elif grid[self.y + dy[dir]][self.x + dx[dir]] == 3 and self.keys > 0:
            #unlock doors
            grid[self.y][self.x] = 0
            self.x += dx[dir]
            self.y += dy[dir]
            grid[self.y][self.x] = 2 
            self.keys -= 1
        elif grid[self.y + dy[dir]][self.x + dx[dir]] == 7:
            grid[self.y][self.x] = 0
            self.x += dx[dir]
            self.y += dy[dir]
            grid[self.y][self.x] = 2
            self.gold += 1
            print(self.gold)
        elif grid[self.y + dy[dir]][self.x + dx[dir]] == 6:
            return True
        
class Grid():
    '''Class that handles all logic to do with the game grid'''
    grid = [[]]
    FOV = 4
    HEIGHT = int
    WIDTH = int
    startRoom = Room
    endRoom = Room
    def __init__(self):
        self.grid, self.roomsList = self.generate_dungeon()
        self.isVisible = [[False] * 32 for _ in range(20)]
        self.fake_grid = [[-1] * 32 for _ in range(20)]

    def spawnEnemies(self):
        enemyList = []
        enemyCount = 3
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
                x = random.randint(0, 31)
                y = random.randint(0, 19)
                if self.grid[y][x] == 0:
                    self.grid[y][x] = 7
                    success = True

    def distance_map(self, player: Player) :
        GRID_HEIGHT = 20
        GRID_WIDTH = 32
        dist_map = [[-1] * GRID_WIDTH for _ in range(GRID_HEIGHT)]

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
                if self.grid[zy][zx] == 0 and dist_map[zy][zx] == -1:
                    dist_map[zy][zx] = dist_map[y][x] + 1
                    queue.append((zx, zy))
        return dist_map

    def visionMap(self):
        highlight = [[0] * 32 for _ in range(20)]
        return

    def updateVisibility(self, player: Player): #updates visible tiles
        for i in range(player.y-4, player.y+5):
            for j in range(player.x-4, player.x+5):
                if 0 <= i < 20 and 0 <= j < 32:
                    self.isVisible[i][j] = True
    
    def gridProxy(self): #returns proxy grid with limited FOV
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
        ROOM_COUNT = 8
        MIN_WIDTH = 4
        MIN_HEIGHT = 4
        MAX_WIDTH = 7
        MAX_HEIGHT = 7

        grid = [[1] * GRID_WIDTH for _ in range(GRID_HEIGHT)]

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