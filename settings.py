import pygame
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
FONT = pygame.font.match_font('courier')
TILESIZE = 32

#PLAYER SETTINGS                        # BEST COMBO OF VALUES FOUND SO FAR
PLAYER_ACCELERATION = 2.5               #   2.5
GRAVITY_MAGNITUDE = 5                   #   5.0
BOUNCE_MAGNITUDE = 40                   #  40.0
WALL_FRICTION = -0.4                    # - 0.4
DRAG = 0.5                              #   0.5
MAX_FALL_VELOCITY = 20                  #  20.0
MAX_JUMP_VELOCITY = 100                 # 100.0
PLAYER_JUMP = 20                        #  20.0
ENERGY_REGEN = 0.5




# Joystick Buttons
JOYSTICK = {'A': 11,
            'B': 12,
            'X': 13,
            'Y': 14,
            'LeftTrigger': 4,
            'RightTrigger': 5}

# controller dictionary
CONTROLLER = {}

CONTROLLER['joystick'] = {}

CONTROLLER['keyboard'] = {}




