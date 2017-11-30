from tkinter import *
from Game import Game, Agent
from geometry import Point2D, Vector2D
import math
import random
import time

TIME_STEP = 0.5

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

class MovingBody(Agent):

    def __init__(self, p0, v0, world):
        self.velocity = v0
        self.accel    = Vector2D(0.0,0.0)
        Agent.__init__(self,p0,world)

    def color(self):
        return "#000080"

    def shape(self):
        p1 = self.position + Vector2D( 0.125, 0.125)       
        p2 = self.position + Vector2D(-0.125, 0.125)        
        p3 = self.position + Vector2D(-0.125,-0.125)        
        p4 = self.position + Vector2D( 0.125,-0.125)
        return [p1,p2,p3,p4]

    def steer(self):
        return Vector2D(0.0)

    def update(self):
        self.position = self.position + self.velocity * TIME_STEP
        self.velocity = self.velocity + self.accel * TIME_STEP
        self.accel    = self.steer()
        self.world.trim(self)

gameWorld = [ [ 1 for x in range(45) ] for x in range(60) ]

for x in range(5, 40):
    gameWorld[x][23] = 0
    
# random segment generator
for q in range(0, 25):
    x = random.randint(0, 59)
    y = random.randint(0, 44)
    upDown = random.randint(0,1)
    howFar = random.randint(0, 40)
    if upDown == 0:
        for l in range(0, howFar):
            gameWorld[x][y - l] = 0
    else:
        for l in range(0, howFar):
            gameWorld[x - l][y] = 0

class Nugget(MovingBody):
    def __init__(self, world, x, y):
        position0 = Point2D(x, y)
        MovingBody.__init__(self, position0, Vector2D(0), world)

    def color(self):
        return "#F0C080"
    
    def remove(self):
        for i, nugget in enumerate(self.world.nuggets):
            if self == nugget:
                # move nugget to somewhere else
                self.world.nuggets[i].position = Point2D(30, 22)


class Wall(MovingBody):
    def __init__(self, world, x, y):
        position0 = Point2D(x, y)
        MovingBody.__init__(self, position0, Vector2D(0), world)

    def shape(self):
        p1 = self.position + Vector2D(.5,.5)       
        p2 = self.position + Vector2D(-.5, .5)        
        p3 = self.position + Vector2D(-.5, -.5)        
        p4 = self.position + Vector2D(.5, -.5)
        return [p1,p2,p3,p4]

    def color(self):
        return "blue"
    
class PacMan(MovingBody):
    
    ACCELERATION   = 0.0
    MAX_SPEED      = 2.0

    def __init__(self,world):
        position0    = Point2D(0,0)
        velocity0    = Vector2D(.5,0.0)
        MovingBody.__init__(self,position0,velocity0,world)
        self.speed   = 0.0
        self.impulse = 0
        self.angle = 90
        self.direction = 'left'

    def color(self):
        return "#F0C080"
    
    def get_heading(self):
        angle = self.angle * math.pi / 180.0
        return Vector2D(math.cos(angle), math.sin(angle))

    def shape(self):
        h  = self.get_heading()
        hp = h.perp()
        pacShape = []
        pacShape.append(self.position + Vector2D(-.25, -.5))
        pacShape.append(self.position + Vector2D(.25, -.5))
        pacShape.append(self.position + Vector2D(.5, -.25))
        pacShape.append(self.position + Vector2D(.5, .25))
        pacShape.append(self.position + Vector2D(.25, .5))
        pacShape.append(self.position + Vector2D(-.25, .5))
        pacShape.append(self.position + Vector2D(-.5, .25))
        pacShape.append(self.position + Vector2D(-.5, -.25))
        if self.direction == 'right':
            pacShape.insert(3, self.position + Vector2D(0,0))
        elif self.direction == 'up':
            pacShape.insert(5, self.position + Vector2D(0,0))
        elif self.direction == 'left':
            pacShape.insert(7, self.position + Vector2D(0,0))
        elif self.direction == 'down':
            pacShape.insert(1, self.position + Vector2D(0,0))
        return pacShape
        
    def turn_left(self):
        self.direction = 'left'

    def turn_right(self):
        self.direction = 'right'

    def turn_up(self):
        self.direction = 'up'

    def turn_down(self):
        self.direction = 'down'

    def update(self):
        MovingBody.update(self)
        x = int(translate(self.position.x, 0, 60, -30, 30))
        y = int(translate(self.position.y, 0, 45, -22.5, 22.5))
        if self.direction == 'left':
            x -= 1
            if gameWorld[x][y] == 1:
                self.velocity = Vector2D(0)            
            else:
                self.velocity = Vector2D(-0.5,0)
        elif self.direction == 'right':
            x += 1
            if gameWorld[x][y] == 1:
                self.velocity = Vector2D(0)            
            else:
                self.velocity = Vector2D(0.5,0)
        elif self.direction == 'up':
            y += 1
            if gameWorld[x][y] == 1:
                self.velocity = Vector2D(0)            
            else:
                self.velocity = Vector2D(0,0.5)
        elif self.direction == 'down':
            y -= 1
            if gameWorld[x][y] == 1:
                self.velocity = Vector2D(0)            
            else:
                self.velocity = Vector2D(0,-0.5)
        # check to see if pac man has eaten any of the nuggets
        for nugget in self.world.nuggets:
            if (nugget.position - self.position).magnitude() < 1:
                self.world.addPoints(1)
                nugget.remove()
                
class PlayPacMan(Game):

    DELAY_START      = 150
    MAX_ASTEROIDS    = 6
    INTRODUCE_CHANCE = 0.01
    
    def __init__(self):
        Game.__init__(self,"PACMAN!!!",60.0,45.0,800,600,topology='wrapped')

        self.level = 1
        self.score = 0

        self.before_start_ticks = self.DELAY_START
        self.started = False

        self.PacMan = PacMan(self)

        self.nuggets = []
        self.walls = []

        counter = 0
        for x, r in enumerate(gameWorld):
            for y, c in enumerate(r):
                h = translate(x, 0, 60, -30, 30)
                v = translate(y, 0, 45, -22, 22) - 0.5
                if gameWorld[x][y] == 0:
                    self.nuggets.append(Nugget(self, h, v))
                else:
                    self.walls.append(Wall(self, h, v))

    def addPoints(self, p):
        self.score += 1
        print(self.score)
                    

    def handle_keypress(self,event):
        Game.handle_keypress(self,event)
        if event.char == 'i':
            self.PacMan.speed_up()
        elif event.char == 'a':
            self.PacMan.turn_left()
        elif event.char == 'd':
            self.PacMan.turn_right()
        elif event.char == 'w':
            self.PacMan.turn_up()
        elif event.char == 's':
            self.PacMan.turn_down()
        
        
    def update(self):
        # Are we waiting to toss asteroids out?
        if self.before_start_ticks > 0:
            self.before_start_ticks -= 1
        else:
            self.started = True
        self.display = 'score: ' + str(self.score)
        Game.update(self)
        

game = PlayPacMan()
while not game.GAME_OVER:
    time.sleep(1.0/60.0)
    game.update()