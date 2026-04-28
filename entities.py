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
        #move in direction
        grid[self.y][self.x] = 0  # clear old position
        self.x += dx[dir]
        self.y += dy[dir]
        grid[self.y][self.x] = 4  # set new position
        return grid

        
    #aggro

    def shortest_path(self):
        pass    
    #sight
    def sight(self, grid):
        pass
    #damage

class Keys():
    def __init__(self):
        pass

    #collision function
    #delete function

class Doors():
    def __init__(self):
        pass

def shortestPath():
    return None
# A point in a Maze (Needed for QNode)
class Point:
    def __init__(self, x_, y_):
        self.x = x_
        self.y = y_

# A QNode (Needed for BFS)
class QNode:
    def __init__(self, p_, d_):
        self.p = p_
        self.d = d_


def is_valid(x, y, r, c):
    return 0 <= x < r and 0 <= y < c


def bfs(mat, src, dest):
    r, c = len(mat), len(mat[0])
    
    # If Source and Destination are valid
    if not mat[src.x][src.y] or not mat[dest.x][dest.y]: return -1

    # Do BFS using Queue and Visited
    vis = [[False] * c for _ in range(r)]
    from collections import deque
    q = deque([QNode(src, 0)])
    vis[src.x][src.y] = True
    while q:
        
        # Pop an item from queue
        node = q.popleft()
        p = node.p
        d = node.d

        # If we reached the destination
        if p.x == dest.x and p.y == dest.y: return d
        
        # Try all four adjacent
        dx = [-1, 0, 0, 1]
        dy = [0, -1, 1, 0]
        for i in range(4):
            nx, ny = p.x + dx[i], p.y + dy[i]
            if is_valid(nx, ny, r, c) and mat[nx][ny] and not vis[nx][ny]:
                vis[nx][ny] = True
                q.append(QNode(Point(nx, ny), d + 1))
    return -1
