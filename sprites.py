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
        self.friction = settings.BLOCKS[self.name]['friction']
        self.bounce = settings.BLOCKS[self.name]['bounce']
        self.death = settings.BLOCKS[self.name]['death']


class AbilityBlock(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h, name):
        self.groups = game.all_sprites, game.abilities
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = game.powerup_img
        self.rect = pygame.Rect(x, y, w, h)
        self.name = name








