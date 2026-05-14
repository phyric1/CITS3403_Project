import random
from flask import request, jsonify
from entities import Enemy, Gold, Goblin
from cards_logic import PlayerDeck
import cards_logic
from collections import deque
from app.utils import get_user_deck
import app.enums

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

#delete strip mine
#delete dash attack
#delete gust
#delete bear trap
class DungeonGame():
    '''class representing a game instance and all its properties'''
    def __init__(self, difficulty):
        #used to start game
        self.player = Player(0, 0)
        self.turnNum = 0
        self.difficulty = difficulty
        self.level = 0
        self.maxLevels = 0

        self.generate_floor(self.level)
        self.turnNum = 0
        self.isVisible = True
        self.filter = [[0] * 32 for _ in range(20)]


        self.timeStopped = False
        self.tailwind = 0

        self.playerDeck: PlayerDeck
        self.hand = []
        self.card_data = None
        self.waiting_for_tile_click = False
        self.pending_card = None

    def dificulty_modifier(self):
        '''Adjusts dungeon based on dificulty'''
        if self.difficulty == "Easy":
                self.maxLevels = 2
                self.darknessChance = 0.01
        if self.difficulty == "Medium":
                self.maxLevels = 4
                self.darknessChance = 0.4
        if self.difficulty == "Hard":
                self.maxLevels = 6
                self.darknessChance = 0.7
        #chance of darkness
        #number of enemies
        pass

    def displayGame(self):
    #returns json information for the game in its current state
        self.grid.updateVisibility(self.player)
        if self.isVisible:
            grid = self.grid.grid
        else:
            grid = self.grid.gridProxy()
        discard_data = self.playerDeck.serialize_card(self.playerDeck.discard[-1]) if self.playerDeck.discard else None
        return jsonify({
                    "grid": grid,
                    "filter": self.filter,
                    "turn": self.turnNum,
                    "hp": self.player.health,
                    "keys": self.player.keys,
                    "gold": self.player.gold,
                    "stealth": self.player.stealth,
                    "floor": self.level,
                    "cards": self.card_data,
                    "discard": discard_data,
                    "deckMax": self.playerDeck.deckMax,
                    "deckSize": self.playerDeck.deckSize,
                })

    def gameOver(self):
        #game over screen and reset button
        print("game over")
        #display game over
        #disable inputs
        #return return stats
        #gold collected, floors cleared, whether dungeon was cleared, which type of dungeon, enemies killed, number of turns played

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
                radius = 3
                x = self.player.x
                y = self.player.y
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        if abs(dy) + abs(dx) <= radius:
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < 20 and 0 <= nx < 32 and self.grid.grid[ny][nx] == 0:
                                self.filter[ny][nx] = 5
                self.waiting_for_tile_click = True
                self.pending_card = "Acrobatics"
            case "Sprint":
                x = self.player.x
                y = self.player.y
                dx = [-1, 1, 0, 0]
                dy = [0, 0, -1, 1]
                for dir in range(4):
                    collide = False
                    i = 0
                    while not collide:
                        i += 1
                        if self.grid.grid[y + dy[dir]*i][x + dx[dir]*i] == 1:
                             collide = True
                        else:
                            self.filter[y + dy[dir]*i][x + dx[dir]*i] = 5
                self.waiting_for_tile_click = True
                self.pending_card = "Sprint"
            case "Timestop":
                self.timeStopped = True
            case "Rest":
                self.player.health += 1
            case "Heal":
                self.player.health += 2
            case "Guard":
                self.player.dodgeChance += 0.05
            case "Parry":
                self.player.dodgeChance += 0.1
            case "Strength":
                self.player.attackDamage += 1
            case "Slingshot":
                radius = 3
                x = self.player.x
                y = self.player.y
                i = 0
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        if abs(dy) + abs(dx) <= radius:
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < 20 and 0 <= nx < 32 and self.grid.grid[ny][nx] == 4:
                                self.filter[ny][nx] = 5
                                i += 1
                if i == 0:
                    return None
                self.waiting_for_tile_click = True
                self.pending_card = "Slingshot"
            case "Dexterity":
                self.player.attackRange += 1
            case "Dagger":
                x = self.player.x
                y = self.player.y
                dx = [-1, 1, 0, 0]
                dy = [0, 0, -1, 1]
                for dir in range(4):
                    #if self.grid.grid[y + dy[dir]][x + dx[dir]] == 4: 
                        self.filter[y + dy[dir]][x + dx[dir]] = 5
                self.waiting_for_tile_click = True
                self.pending_card = "Dagger"
            case "Dash Attack": #like sprint but deals damage to all enemies in path
                self.waiting_for_tile_click = True
                self.pending_card = "Dash Attack"
            case "Meteor": #locate all enemies and rturn their tiles
                for enemy in self.enemies:
                    self.filter[enemy.y][enemy.x] = 5
                self.waiting_for_tile_click = True
                self.pending_card = "Meteor"
            case "Flash": #deaggros all enemies in an area around the player
                radius = 3
                x = self.player.x
                y = self.player.y
                for enemy in self.enemies:
                    if abs(enemy.y - y) + abs(enemy.x - x) <= radius:
                        enemy.state = "idle"
            case "Silence Falls":
                self.player.stealth += 1
            case "Shadow Sneak":
                self.player.stealth += 2
            case "Dynamite":
                grid = self.grid.grid
                radius = 2
                x = self.player.x
                y = self.player.y
                min_y = max(0, y - radius)
                max_y = min(len(grid) - 1, y + radius)
                min_x = max(0, x - radius)
                max_x = min(len(grid[0]) - 1, x + radius)
                for i in range(min_y, max_y + 1):
                    for j in range(min_x, max_x + 1):
                        if grid[i][j] == 1:
                            grid[i][j] = 0
                for enemy in self.enemies:
                    if min_x <= enemy.x <= max_x and min_y <= enemy.y <= max_y:
                        defeated = enemy.takeDamage(4)
                        if defeated:
                            self.grid.grid[enemy.y][enemy.x] = 0
                            self.enemies.remove(enemy)
                            self.player.gold += 1
            case "Eye for Treasure":
                self.grid.spawnGold(1)
            case "Light the Way":
                self.isVisible = True
            case "Key to Victory":
                self.player.keys += 1
            case "Recycle":
                self.playerDeck.deck.append(self.playerDeck.discard[0])
                self.playerDeck.deckSize = len(self.playerDeck.deck)
        if card.card.type == app.enums.CardType.survival and 'Master of Survival' in self.playerDeck.master_cards:
            self.player.health += 1
        if card.card.type == app.enums.CardType.movement and 'Master of Movement' in self.playerDeck.master_cards:
            self.player.stealth += 1
        return card

    def generate_floor(self, level): #generates a new dungeon floor
        if level == 0: #first level is always visible
            self.isVisible = True
        self.grid = Grid(33, 20, 4)
        x, y = self.grid.startRoom.center()
        self.player.x, self.player.y = x, y
        self.enemies = [] #new enemies on each floor
        self.enemies = self.grid.spawnEnemies()
        self.grid.spawnGold(2)
        self.level += 1

    def process_tile_click(self, x, y):
        if self.pending_card == "Sprint":
            # move player to x, y
            self.grid.grid[self.player.y][self.player.x] = 0
            self.player.x = x
            self.player.y = y
            self.grid.grid[y][x] = 2
        elif self.pending_card == "Acrobatics":
            # move player to x, y
            self.grid.grid[self.player.y][self.player.x] = 0
            self.player.x = x
            self.player.y = y
            self.grid.grid[y][x] = 2
        elif self.pending_card == "Dagger":
            # move player to x, y
            for enemy in self.enemies:
                if enemy.x == x and enemy.y == y:
                    defeated = enemy.takeDamage(self.player.attackDamage)
                    if defeated:
                        self.grid.grid[enemy.y][enemy.x] = 0
                        self.enemies.remove(enemy)
                        self.player.gold += 1
                    break
        elif self.pending_card == "Meteor":
            for enemy in self.enemies:
                if enemy.x == x and enemy.y == y:
                    defeated = enemy.takeDamage(4)
                    if defeated:
                        self.grid.grid[enemy.y][enemy.x] = 0
                        self.enemies.remove(enemy)
                        self.player.gold += 1
                    break
        elif self.pending_card == "Slingshot":
            for enemy in self.enemies:
                if enemy.x == x and enemy.y == y:
                    defeated = enemy.takeDamage(self.player.attackDamage)
                    if defeated:
                        self.grid.grid[enemy.y][enemy.x] = 0
                        self.enemies.remove(enemy)
                        self.player.gold += 1
                    break

    def advance_game(self, input):
        '''advances the game by one turn'''
        self.filter = [[0] * 32 for _ in range(20)]
        grid = self.getGrid()
        discard_data = None
        newFloor = False
        input_type = input.get("type")
        if input_type == "move":
            newFloor = self.player.movePlayer(input.get("direction"), grid)  #move player
        elif input_type == "pick_card" and self.tailwind == 0:
            if self.hand:
                card = self.cardProcessor(self.playerDeck.useSlot(int(input.get("slot"))))
                discard_data = self.playerDeck.serialize_card(card)
                #all cards flip over
                #card is already sent to discard slot
                #load new grid data
                #activate new event listeners
                #upon new input, increment turn and continue advancing the game
        elif input_type == "tile_click":
            x = input.get("x")
            y = input.get("y")
            if self.waiting_for_tile_click:
                self.process_tile_click(x, y)
                self.waiting_for_tile_click = False
                self.pending_card = None

        #flow control module for card effects that last multiple turns or require player input
        if self.tailwind > 0:
            self.tailwind -= 1
            self.getGridObject().updateVisibility(self.player)
            self.turnNum += 1 #increment turn count unless card effect overrides it
            return self.displayGame()

        if self.waiting_for_tile_click: #2 phase card, end turn early and wait for tile click input before advancing game state
            return self.displayGame()
        #upon picking a 2 phase card, a description of what to do appears where the hand usually is
        #game over goes here as well

        self.playerDeck.hand = self.playerDeck.shuffle(self.playerDeck.deck) #move logic to cards file
        self.card_data = [self.playerDeck.serialize_card(card) for card in self.playerDeck.hand]

        if newFloor:
            self.timeStopped = False
            self.generate_floor(self.level)
            self.getGridObject().updateVisibility(self.player)
            self.turnNum += 1
            return self.displayGame()
        
        if not self.timeStopped:
            for enemy in self.enemies: #move enemies
                enemy.moveEnemy(grid, self.grid.distance_map(self.player), self.filter)
                if enemy.state == "chase" and self.player.stealth > 0:
                    self.player.stealth -= 1
                    enemy.state = "idle"
                enemy.attack(self.player)
                if self.player.health <= 0:
                    self.gameOver()
        self.turnNum += 1
        self.getGridObject().updateVisibility(self.player)
        return self.displayGame()
    
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
        self.attackRange = 1
        self.dodgeChance = 0.0

    def takeDamage(self, damage):
        if self.dodgeChance < random.random():
            self.health -= damage
        else:
            print("dodge")
        return self.health
    
    def alert(self): #alerts surrounding enemies
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
        
        move = False
        newFloor = False
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
        elif grid[self.y + dy[dir]][self.x + dx[dir]] == 8:
            #final chest, end the game
            move = True
        if move:
            grid[self.y][self.x] = 0
            self.x += dx[dir]
            self.y += dy[dir]
            grid[self.y][self.x] = 2
        if newFloor:
            return True
        
        
class Grid():
    '''Class that handles all logic to do with the game grid'''
    startRoom = Room
    endRoom = Room
    def __init__(self, WIDTH, HEIGHT, FOV):
        self.HEIGHT = HEIGHT
        self.WIDTH = WIDTH
        self.FOV = FOV
        self.grid, self.roomsList = self.generate_dungeon()
        self.isVisible = [[False] * self.WIDTH for _ in range(self.HEIGHT)]
        self.fake_grid = [[-1] * self.WIDTH for _ in range(self.HEIGHT)]

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
        for i in range(0,20):
            for j in range(0,32):
                if self.isVisible[i][j]:
                    self.fake_grid[i][j] = self.grid[i][j]
                else:
                    self.fake_grid[i][j] = -1
        return self.fake_grid

    def generate_dungeon(self):    
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