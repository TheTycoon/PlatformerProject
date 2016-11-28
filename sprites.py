import pygame
import settings


class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h, name):
        self.groups = game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.name = name
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

BLOCKS['jump'] = {'friction': settings.WALL_FRICTION,
                  'bounce': settings.BOUNCE_MAGNITUDE,
                  'death': False}

BLOCKS['death'] = {'friction': 0,
                   'bounce': 0,
                   'death': True}









