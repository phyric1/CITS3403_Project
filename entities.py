import random

class Enemy():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        #left = 0, right = 1, up = 2, down = 3
        self.direction = 0
        self.state = "idle" 
        self.health = 1
        self.maxHealth = self.health

    def takeDamage(self, damage):
        self.health -= damage
        return self.health <= 0

    def moveEnemy(self, grid, dist_map, filter):
        if self.state == "idle":
            f, alert = self.patrol(grid, filter)
            if alert:
                return alert
        elif self.state == "chase":
            self.chase(grid, dist_map)

    def patrol(self, grid, filter):
        dir = self.direction #current direction
        other_dir = [0, 1, 2, 3] 
        if dir in other_dir:
            other_dir.remove(dir) #list of other directions

        #directions
        dx = [-1, 1, 0, 0]
        dy = [0, 0, -1, 1]
        
        #determine if current direction is occupied
        if grid[self.y + dy[dir]][self.x + dx[dir]] != 0: 
            #randomly pick new direction to patrol
            clear_path = False
            while not clear_path and len(other_dir) > 0:
                dir = other_dir[random.randint(0, len(other_dir)-1)]
                if grid[self.y + dy[dir]][self.x + dx[dir]] != 0: 
                    other_dir.remove(dir)
                else:
                    clear_path = True
                    self.direction = dir
                    #consider moving away from other enemies when patroling
        #move in direction
        grid[self.y][self.x] = 0  # clear old position
        self.x += dx[dir]
        self.y += dy[dir]
        grid[self.y][self.x] = 4  # set new position
        new_filter, alert = self.detect(grid, filter)
        if alert:
            return new_filter, True
        return new_filter, False
         
    #aggressive
    def chase(self, grid, dist_map):
        best_dir = -1
        best_dist = 999
        #directions
        dx = [-1, 1, 0, 0]
        dy = [0, 0, -1, 1]

        for i in range(4):
            d = dist_map[self.y + dy[i]][self.x + dx[i]]
            if d < best_dist and d != -1:
                best_dist = dist_map[self.y + dy[i]][self.x + dx[i]]
                best_dir = i
        if best_dir == -1:
            return grid
        self.direction = best_dir
        if grid[self.y + dy[best_dir]][self.x + dx[best_dir]] == 2:
            return grid
        grid[self.y][self.x] = 0  # clear old position
        self.x += dx[best_dir]
        self.y += dy[best_dir]
        grid[self.y][self.x] = 4
        return grid
    
    #add los check
    def detect(self, grid, filter):
        vision_width = 5
        vision_depth = 5
        halfW = vision_width // 2

        if self.direction == 1: #right
            if grid[self.y][self.x+1] != 1:
                for y in range(self.y - halfW, self.y + halfW + 1):
                    for x in range(self.x + 1, self.x + vision_depth):
                        if self.bounds_check(filter, x, y):
                            if grid[y][x] == 1:
                                break
                            elif grid[y][x] == 2:
                                self.state = "chase"
                                return filter, True
                            else:
                                filter[y][x] = 1
        elif self.direction == 0: #left
            if grid[self.y][self.x-1] != 1:
                for y in range(self.y - halfW, self.y + halfW + 1):
                    zx = self.x - 1
                    for x in range(vision_depth):
                        if self.bounds_check(filter, zx, y):
                            if grid[y][zx] == 1:
                                break
                            elif grid[y][zx] == 2:
                                self.state = "chase"
                                return filter, True
                            else:
                                filter[y][zx] = 1
                                zx -= 1
        elif self.direction == 2: #up
            if grid[self.y - 1][self.x] != 1:
                for x in range(self.x - halfW, self.x + halfW + 1):
                    zy = self.y - 1
                    for y in range(vision_depth):
                        if self.bounds_check(filter, x, zy):
                            if grid[zy][x] == 1:
                                break
                            elif grid[zy][x] == 2:
                                self.state = "chase"
                                return filter, True
                            else:
                                filter[zy][x] = 1
                                zy -= 1
        elif self.direction == 3: #down
            if grid[self.y + 1][self.x] != 1:
                for x in range(self.x - halfW, self.x + halfW + 1):
                    for y in range(self.y + 1, self.y + vision_depth):
                        if self.bounds_check(filter, x, y):
                            if grid[y][x] == 1:
                                break
                            elif grid[y][x] == 2:
                                self.state = "chase"
                                return filter, True
                            else:
                                filter[y][x] = 1
        return filter, False

    def bounds_check(self, filter, x, y):
        if 0 <= y < len(filter) and 0 <= x < len(filter[0]):
            return True
        else:
            return False
    
    def attack(self, player):
        #directions
        dx = [-1, 1, 0, 0]
        dy = [0, 0, -1, 1]        
        for i in range(4):
            if (self.x + dx[i] == player.x and self.y + dy[i] == player.y) or (self.x == player.x and self.y == player.y):
                success = player.takeDamage(1)
                return success
        return False
    
class Goblin(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)