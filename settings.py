import math
# Game Options and Settings

# define colors
WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)
GRAY   = (128, 128, 128)
RED    = (255,   0,   0)
ORANGE = (255, 165,   0)
YELLOW = (255, 255,   0)
GREEN  = (  0, 128,   0)
BLUE   = (  0,   0, 255)
PURPLE = (128,   0, 128)
BROWN  = (165,  42,  42)

# game settings
WIDTH = 640
HEIGHT = 640
FPS = 60
TITLE = 'Platformer Project'
TILESIZE = 32


PLAYER_ACCELERATION = 2
GRAVITY_MAGNITUDE = 1
MAX_VELOCITY = 15
PLAYER_JUMP = 60


# Directions for use in velocity/acceleration vectors
LEFT = 3 * math.pi / 2
RIGHT = math.pi / 2
UP = math.pi
DOWN = 0
