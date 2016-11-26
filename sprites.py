import pygame


class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h, bounce):
        self.groups = game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.bounce = bounce

