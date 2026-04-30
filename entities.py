import random

class Items():
    def __init__(self):
        pass

class Enemy():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        #left = 0, right = 1, up = 2, down = 3
        self.direction = 0
        self.state = "idle" 
        self.health = 1

    def patrol(self, grid):
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
            while not clear_path:
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
        return grid
         
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

        grid[self.y][self.x] = 0  # clear old position
        self.x += dx[best_dir]
        self.y += dy[best_dir]
        grid[self.y][self.x] = 4 
        return grid

    def sight(self, grid):
        self.direction
    
    def attack(self):
        pass

class Hound(Enemy):
    pass

class Trolls(Enemy):
    pass

class Keys():
    def __init__(self):
        pass
    #collision function
    #delete function

class Doors():
    def __init__(self):

        pass