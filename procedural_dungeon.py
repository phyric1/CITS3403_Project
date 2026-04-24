import random
def generate_dungeon():    
    GRID_HEIGHT = 20
    GRID_WIDTH = 28

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
    for i in range(7):
        success = False
        while success == False:
            width = random.randint(4, 8)
            height = random.randint(4, 8)
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
    return grid

gridA = generate_dungeon()
for i in range(20):
   print(gridA[i])

#for each room pair:
#    connect them with corridors








#choose start room
#choose farthest room as end

#mark start and end in grid