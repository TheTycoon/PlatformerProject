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
WIDTH = 1366
HEIGHT = 768
FPS = 60
TITLE = 'Platformer Project'
FONT = pygame.font.match_font('courier')
TILESIZE = 32

#PLAYER SETTINGS                        # BEST COMBO OF VALUES FOUND SO FAR
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 64
PLAYER_ACCELERATION = 2.5               #   2.5
GRAVITY_MAGNITUDE = 5                   #   5.0
BOUNCE_MAGNITUDE = 20                   #  20.0
WALL_FRICTION = -0.4                    # - 0.4
DRAG = 0.5                              #   0.5
MAX_FALL_VELOCITY = 20                  #  20.0
MAX_JUMP_VELOCITY = 100                 # 100.0
PLAYER_JUMP = 20                        #  20.0
ENERGY_REGEN = 0.5
ENERGY_COOLDOWN = 5000                  # time in milliseconds
AIR_DASH_MAGNITUDE = 100                # number of pixels instantly traveled




# Joystick Buttons
JOYBUTTONS = {
            'A'           : 0,
            'B'           : 1,
            'X'           : 2,
            'Y'           : 3,
            'LeftBumper'  : 4,
            'RightBumper' : 5,
            'Back'        : 6,
            'Start'       : 7,
            'LeftStick'   : 8,
            'RightStick'  : 9
           }

JOYAXIS = {
    'LeftHorizontal' : 0,
    'LeftVertical'   : 1,
    'Trigger'        : 2,               # Positive 1 is Left Down, Negative 1 is Right Down
    'RightHorizontal': 3,
    'RightVertical'  : 4
}


# controller dictionary
CONTROLLER = {}

CONTROLLER['joystick'] = {}

CONTROLLER['keyboard'] = {}




