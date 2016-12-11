import pygame
import settings


class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h, name, direction):
        if name == 'wall':
            self.groups = game.blocks, game.walls
        elif name == 'platform':
            self.groups = game.blocks, game.platforms
        else:
            self.groups = game.blocks

        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.name = name
        self.direction = direction
        self.friction = BLOCKS[self.name]['friction']
        self.bounce = BLOCKS[self.name]['bounce']
        self.death = BLOCKS[self.name]['death']


class Interactable(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h, name):
        self.groups = game.interactables
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.name = name


class Ability(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h, name):
        self.groups = game.abilities
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = game.powerup_img
        self.rect = pygame.Rect(x, y, w, h)
        self.name = name


# BLOCK TYPES
# Will convert death blocks to doing damage once the health system is in place
# Some blocks will drain health over time, others will cause instant death
BLOCKS = {}
BLOCKS['wall'] = {'friction': settings.WALL_FRICTION,
                  'bounce': 0,
                  'death': False}

BLOCKS['platform'] = {'friction': settings.WALL_FRICTION,
                      'bounce': 0,
                      'death': False}

BLOCKS['ice'] = {'friction': settings.WALL_FRICTION / 3,
                  'bounce': 0,
                  'death': False}

BLOCKS['bounce'] = {'friction': settings.WALL_FRICTION,
                  'bounce': settings.BOUNCE_MAGNITUDE,
                  'death': False}

BLOCKS['death'] = {'friction': 0,
                   'bounce': 0,
                   'death': True}

BLOCKS['platform'] = {'friction': settings.WALL_FRICTION,
                      'bounce': 0,
                      'death': False}









