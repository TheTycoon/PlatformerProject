import pygame
import settings


class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.friction = settings.WALL_FRICTION
        self.bounce = 0
        self.death = False
        self.type = 'Wall'


class BounceBlock(Wall):
    def __init__(self, game, x, y, w, h):
        Wall.__init__(self, game, x, y, w, h)
        self.bounce = settings.BOUNCE_MAGNITUDE
        self.type = 'Bounce'


class IceBlock(Wall):
    def __init__(self, game, x, y, w, h):
        Wall.__init__(self, game, x, y, w, h)
        self.friction = settings.WALL_FRICTION / 3
        self.type = 'Speed'


class SlowBlock(Wall):
    def __init__(self, game, x, y, w, h):
        Wall.__init__(self, game, x, y, w, h)
        self.friction = 2 * settings.WALL_FRICTION
        self.type = 'Slow'


class DeathBlock(Wall):
    def __init__(self, game, x, y, w, h):
        Wall.__init__(self, game, x, y, w, h)
        self.death = True
        self.type = 'Death'





