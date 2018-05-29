import pygame
import settings


# find a better way to add these single kinds of animations like this and the bullet one which are basically the same
class SingleAnimation(pygame.sprite.Sprite):
    def __init__(self, center, spritesheet, frame_rate):
        pygame.sprite.Sprite.__init__(self)
        self.spritesheet = spritesheet
        self.image = spritesheet[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = frame_rate

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.spritesheet):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.spritesheet[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, center, direction):
        pygame.sprite.Sprite.__init__(self, )
        self.game = game
        self.image = game.yellow_bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.direction = direction

    def update(self):
        # Move bullet and collisions
        if self.direction == 'right':
            self.rect.x += 20
        else:
            self.rect.x -= 20

        for block in self.game.blocks:
            if self.rect.colliderect(block.rect):
                self.kill()


class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h, name, direction):
        if name == 'wall' or name == 'ice':
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
    def __init__(self, game, x, y, w, h, name, img_on, img_off, ability):
        self.groups = game.interactables
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.name = name
        self.image = img_off
        self.image_on = img_on
        self.image_off = img_off
        self.state = False
        self.rect = pygame.Rect(x, y, w, h)
        self.ability = ability

    def update(self):
        if self.state is False:
            self.image = self.image_off
        else:
            self.image = self.image_on

    def handle_event(self):
        pass

# BLOCK TYPES
# Will convert death blocks to doing damage once the health system is in place
# Some blocks will drain health over time, others will cause instant death
# the block names here are used as objects in Tiled
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

BLOCKS['bounce'] = {'friction': 2 * settings.WALL_FRICTION,
                  'bounce': settings.BOUNCE_MAGNITUDE,
                  'death': False}

BLOCKS['death'] = {'friction': 0,
                   'bounce': 0,
                   'death': True}









