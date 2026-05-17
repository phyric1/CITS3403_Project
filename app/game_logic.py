import random
from flask import jsonify
from app.deck import PlayerDeck
from app.grid import Grid
from app.player import Player
import app.enums

class DungeonGame():
    '''class representing a game instance and all its properties'''
    def __init__(self, difficulty):
        self.player = Player(0, 0)
        self.turnNum = 0
        self.difficulty = difficulty
        self.level = 0
        
        self.darknessChance, self.maxLevels = self.dificulty_modifier(difficulty)
        self.isVisible = True
        self.filter = [[0] * 32 for _ in range(20)]
        self.generate_floor(self.level)

        self.timeStopped = False
        self.tailwind = 0

        self.playerDeck: PlayerDeck
        self.hand = []
        self.card_data = None
        self.waiting_for_tile_click = False
        self.pending_card = None
        self.isGameOver = False
        self.isWin = False
        self.gameOverStats = {}
        self.sound_events = []

    def dificulty_modifier(self, difficulty):
        '''Adjusts dungeon based on dificulty'''
        maxLevels = 0
        darknessChance = 0
        if difficulty == "Easy":
            maxLevels = 2
            darknessChance = 0.01
        if difficulty == "Normal":
            maxLevels = 4
            darknessChance = 0.4
        if difficulty == "Hard":
            maxLevels = 6
            darknessChance = 0.7
        return darknessChance, maxLevels

    def displayGame(self):
    #'''returns json information for the game in its current state'''
        self.grid.updateVisibility(self.player)
        if self.isVisible:
            grid = self.grid.grid
        else:
            grid = self.grid.gridProxy()
        self.card_data = [self.playerDeck.serialize_card(card) for card in self.playerDeck.hand]
        discard_data = self.playerDeck.serialize_card(self.playerDeck.discard[-1]) if self.playerDeck.discard else None
        soundEvents = self.sound_events
        self.sound_events = []
        visible_entities = [
            {"type": "player", "x": self.player.x, "y": self.player.y, "direction": self.player.direction}
        ]
        if self.isVisible:
            visible_entities.extend(
                {"type": "enemy", "x": enemy.x, "y": enemy.y, "direction": enemy.direction}
                for enemy in self.enemies
            )
        else:
            visible_entities.extend(
                {"type": "enemy", "x": enemy.x, "y": enemy.y, "direction": enemy.direction}
                for enemy in self.enemies
                if self.grid.isVisible[enemy.y][enemy.x]
            )
        return jsonify({
                    "grid": grid,
                    "filter": self.filter,
                    "entities": visible_entities,
                    "events": soundEvents,
                    "turn": self.turnNum,
                    "hp": self.player.health,
                    "keys": self.player.keys,
                    "gold": self.player.gold,
                    "stealth": self.player.stealth,
                    "floor": self.level,
                    "maxFloors": self.maxLevels,
                    "cards": self.card_data,
                    "discard": discard_data,
                    "deckMax": self.playerDeck.deckMax,
                    "deckSize": self.playerDeck.deckSize,
                    "waitingForTileClick": self.waiting_for_tile_click,
                    "pendingCard": self.pending_card,
                    "isGameOver": self.isGameOver,
                    "isWin": self.isWin,
                    "gameOverStats": self.gameOverStats,
                })

    def won(self):
        '''called when  player reaches the end of the dungeon'''
        self.isGameOver = True
        self.isWin = True
        if self.difficulty == "Easy":
            reward = "Common"
        elif self.difficulty == "Normal":
            reward = "Uncommon"
        elif self.difficulty == "Hard":
            reward = "Rare"
        self.gameOverStats = {
            "status": "win",
            "reward": reward,
            "floorsCleared": self.level,
            "goldCollected": self.player.gold,
            "enemiesDefeated": self.player.enemies_defeated,
            "turnsPlayed": self.turnNum,
            "difficulty": self.difficulty,
        }
        self.emitSoundEvent("game_win")

    def emitSoundEvent(self, event):
        '''adds sound event to be sent to frontend sound player'''
        if event not in self.sound_events:
            self.sound_events.append(event)

    def gameOver(self):
        '''called when game ends'''
        self.isGameOver = True
        self.isWin = False
        self.gameOverStats = {
            "status": "lose",
            "reward": 0,
            "floorsCleared": self.level,
            "goldCollected": self.player.gold,
            "enemiesDefeated": self.player.enemies_defeated,
            "turnsPlayed": self.turnNum,
            "difficulty": self.difficulty,
        }
        self.emitSoundEvent("game_lose")

    def cardProcessor(self, card):
        '''Switch statement to read card name and perform corresponding function'''
        match card.card.name:
            case "Tailwind":
                self.tailwind = 3
            case "Teleport":
                success = False
                while success == False:
                    x = random.randint(0, self.grid.WIDTH - 1)
                    y = random.randint(0, self.grid.HEIGHT - 1)
                    if not self.grid.boundaryCheck(x, y):
                        break
                    if self.grid.grid[y][x] == 0:
                        self.grid.grid[self.player.y][self.player.x] = 0
                        self.player.x, self.player.y = x, y
                        self.grid.grid[y][x] = 2
                        self.emitSoundEvent("flash")
                        success = True
            case "Acrobatics":
                radius = 3
                x = self.player.x
                y = self.player.y
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        if abs(dy) + abs(dx) <= radius:
                            ny, nx = y + dy, x + dx
                            if self.grid.boundaryCheck(nx, ny) and self.grid.grid[ny][nx] == 0:
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
                        if not self.grid.boundaryCheck(x + dx[dir]*i, y + dy[dir]*i):
                            break
                        if self.grid.grid[y + dy[dir]*i][x + dx[dir]*i] == 1:
                             collide = True
                        else:
                            self.filter[y + dy[dir]*i][x + dx[dir]*i] = 5
                self.waiting_for_tile_click = True
                self.pending_card = "Sprint"
            case "Timestop":
                self.emitSoundEvent("flash")
                self.timeStopped = True
            case "Rest":
                self.emitSoundEvent("buff")
                self.player.health += 1
            case "Heal":
                self.emitSoundEvent("buff")
                self.player.health += 2
            case "Guard":
                self.player.dodgeChance += 0.05
            case "Parry":
                self.player.dodgeChance += 0.1
            case "Strength":
                self.emitSoundEvent("buff")
                self.player.attackDamage += 1
            case "Slingshot":
                radius = 2 + self.player.attackRange
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
                self.emitSoundEvent("buff")
                self.player.attackRange += 1
            case "Dagger":
                x = self.player.x
                y = self.player.y
                dx = [-1, 1, 0, 0]
                dy = [0, 0, -1, 1]
                i = 0
                for dir in range(4):
                    for dist in range(1, self.player.attackRange + 1):
                        ny = y + dy[dir] * dist
                        nx = x + dx[dir] * dist
                        if not self.grid.boundaryCheck(nx, ny):
                            break
                        if self.grid.grid[ny][nx] == 4:
                            self.filter[ny][nx] = 5
                            i += 1
                if i == 0:
                    return None
                self.waiting_for_tile_click = True
                self.pending_card = "Dagger"
            case "Meteor":
                for enemy in self.enemies:
                    self.filter[enemy.y][enemy.x] = 5
                self.waiting_for_tile_click = True
                self.pending_card = "Meteor"
            case "Flash": #de-aggros all enemies in an area around the player
                self.emitSoundEvent("flash")
                radius = 3
                x = self.player.x
                y = self.player.y
                for enemy in self.enemies:
                    if abs(enemy.y - y) + abs(enemy.x - x) <= radius:
                        enemy.state = "idle"
            case "Dynamite":
                grid = self.grid.grid
                radius =  + self.player.attackRange
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
                    self.emitSoundEvent("explosion")
                    if min_x <= enemy.x <= max_x and min_y <= enemy.y <= max_y:
                        defeated = enemy.takeDamage(4)
                        if defeated:
                            self.enemy_defeat(enemy)
            case "Fighting Spirit":
                self.playerDeck.combat_bonus += 0.2
            case "Silence Falls":
                self.player.stealth += 1
            case "Shadow Sneak":
                self.player.stealth += 2
            case "Eye for Treasure":
                self.grid.spawnGold(1)
            case "Light the Way":
                self.emitSoundEvent("flash")
                self.isVisible = True
            case "Key to Victory":
                self.player.keys += 1
            case "Recycle":
                if self.playerDeck.discard:
                    recycled_card = self.playerDeck.discard.pop(0)
                    self.playerDeck.deck.append(recycled_card)
                    self.playerDeck.deckSize = len(self.playerDeck.deck)
        if card.card.type == app.enums.CardType.survival and "Master of Survival" in self.playerDeck.master_cards:
            self.player.health += 1
        if card.card.type == app.enums.CardType.movement and "Master of Movement" in self.playerDeck.master_cards:
            self.player.stealth += 1
        if "Master of Cards" in self.playerDeck.master_cards:
            if card in self.playerDeck.discard and random.random() < 0.15:
                self.playerDeck.discard.remove(card)
                self.emitSoundEvent("floor_cleared")
                self.emitSoundEvent("card_play")
                self.playerDeck.deck.append(card)
                self.playerDeck.deckSize = len(self.playerDeck.deck)
        return card

    def generate_floor(self, level):
        '''generates a new dungeon floor'''
        if level == 0: #first level is always visible
            self.isVisible = True
        else:
            if self.darknessChance > random.random():
                self.isVisible = False
        if level == self.maxLevels - 1:
            self.grid = Grid(33, 20, 4, True)
        else:
            self.grid = Grid(33, 20, 4, False)
        x, y = self.grid.startRoom.center()
        self.player.x, self.player.y = x, y
        self.enemies = [] #new enemies on each floor
        if self.difficulty == "Easy":
            if level == 0:
                self.enemies = self.grid.spawnEnemies(1, 1)
            else:
                self.enemies = self.grid.spawnEnemies(1, 1)
            self.grid.spawnGold(2)
        if self.difficulty == "Normal":
            if level < self.maxLevels - 1:
                self.enemies = self.grid.spawnEnemies(3, 1)
            if level == self.maxLevels - 1:
                self.enemies = self.grid.spawnEnemies(3, 2)
            self.grid.spawnGold(2 + level//2)
        if self.difficulty == "Hard":
            if level == 0:
                self.enemies = self.grid.spawnEnemies(3, 2)
            elif level < self.maxLevels - 2:
                self.enemies = self.grid.spawnEnemies(4, 3)
            elif level == self.maxLevels - 1:
                self.enemies = self.grid.spawnEnemies(5, 4)
            self.grid.spawnGold(2 + level//2)
        self.level += 1

    def process_tile_click(self, x, y):
        action_performed = False
        if self.pending_card == "Sprint":
            self.grid.grid[self.player.y][self.player.x] = 0
            self.player.x = x
            self.player.y = y
            self.grid.grid[y][x] = 2
            action_performed = True
            self.emitSoundEvent("player_move")
        elif self.pending_card == "Acrobatics":
            self.grid.grid[self.player.y][self.player.x] = 0
            self.player.x = x
            self.player.y = y
            self.grid.grid[y][x] = 2
            action_performed = True
            self.emitSoundEvent("player_move")
        elif self.pending_card == "Dagger":
            for enemy in self.enemies:
                if enemy.x == x and enemy.y == y:
                    defeated = enemy.takeDamage(self.player.attackDamage)
                    self.emitSoundEvent("attack")
                    if defeated:
                        self.enemy_defeat(enemy)
                    action_performed = True
                    break
        elif self.pending_card == "Meteor":
            for enemy in self.enemies:
                if enemy.x == x and enemy.y == y:
                    defeated = enemy.takeDamage(4)
                    self.emitSoundEvent("explosion")
                    if defeated:
                        self.enemy_defeat(enemy)
                    action_performed = True
                    break
        elif self.pending_card == "Slingshot":
            for enemy in self.enemies:
                if enemy.x == x and enemy.y == y:
                    defeated = enemy.takeDamage(self.player.attackDamage)
                    self.emitSoundEvent("attack")
                    if defeated:
                        self.enemy_defeat(enemy)
                    action_performed = True
                    break
        return action_performed

    def enemy_defeat(self, enemy):
        '''Triggers game events for when an enemy reaches 0 health'''
        self.grid.grid[enemy.y][enemy.x] = 0
        if enemy in self.enemies:
            self.enemies.remove(enemy)
        self.player.enemies_defeated += 1
        reward = 1
        if "Master of Combat" in self.playerDeck.master_cards:
            self.emitSoundEvent("pickup")
            reward += enemy.maxHealth
        self.player.gold += reward
        self.emitSoundEvent("enemy_defeat")

    def advance_game(self, input):
        '''advances the game by one turn'''
        self.filter = [[0] * 32 for _ in range(20)]
        grid = self.getGrid()
        newFloor = False
        input_type = input.get("type")
        if input_type == "move":
            newFloor, won, moved, tile = self.player.movePlayer(input.get("direction"), grid)  #move player
            if moved:
                if tile == 0 or tile == 3:
                    self.emitSoundEvent("player_move")
                elif tile == 7 or tile == 5:
                    self.emitSoundEvent("pickup")
                elif tile == 6:
                    self.emitSoundEvent("floor_cleared")
            if won:
                self.won()
                return self.displayGame()
        elif input_type == "pick_card" and self.tailwind == 0:
            self.emitSoundEvent("play_card")
            if self.hand:
                card = self.cardProcessor(self.playerDeck.useSlot(int(input.get("slot"))))
                try:
                    if card and getattr(card, 'card', None):
                        type = card.card.type
                        if type == app.enums.CardType.combat:
                            self.playerDeck.combat_counter += 1
                        elif type == app.enums.CardType.movement:
                            self.playerDeck.movement_counter += 1
                        elif type == app.enums.CardType.survival:
                            self.playerDeck.survival_counter += 1
                        elif type == app.enums.CardType.utility:
                            self.playerDeck.utility_counter += 1
                except Exception:
                    pass
        elif input_type == "tile_click":
            x = input.get("x")
            y = input.get("y")
            if self.waiting_for_tile_click:
                if self.process_tile_click(x, y):
                    self.waiting_for_tile_click = False
                    self.pending_card = None
                else:
                    return self.displayGame()

        #flow control module for card effects that last multiple turns or require player input
        if self.tailwind > 0:
            self.tailwind -= 1
            self.getGridObject().updateVisibility(self.player)
            self.turnNum += 1 #increment turn count unless card effect overrides it
            return self.displayGame()

        if self.waiting_for_tile_click: #2 phase card, end turn early and wait for tile click input before advancing game state
            return self.displayGame()

        self.playerDeck.hand = self.playerDeck.shuffle(self.playerDeck.deck)
        self.card_data = [self.playerDeck.serialize_card(card) for card in self.playerDeck.hand]

        if newFloor:
            self.timeStopped = False
            self.generate_floor(self.level)
            self.getGridObject().updateVisibility(self.player)
            self.turnNum += 1
            return self.displayGame()
        
        if not self.timeStopped:
            for enemy in self.enemies: #move enemies
                if enemy.moveEnemy(grid, self.grid.distance_map(self.player), self.filter):
                    self.emitSoundEvent("alert")
                if enemy.state == "chase" and self.player.stealth > 0:
                    self.player.stealth -= 1
                    enemy.state = "idle"
                if enemy.attack(self.player):
                    self.emitSoundEvent("player_hurt")
                elif enemy.attack(self.player) == False:
                    self.emitSoundEvent("guard")
                if self.player.health <= 0:
                    self.gameOver()
                    return self.displayGame()
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
    