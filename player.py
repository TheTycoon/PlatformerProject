import pygame
import settings
import math


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((32, 32))
        self.rect = self.image.get_rect()
        self.image.fill(settings.BLUE, self.rect)
        self.x = x
        self.y = y
        self.rect.topleft = (self.x, self.y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.jumping = False


    def move(self, dx, dy):
        # Move each axis separately. Note that this checks for collisions both times.
        if dx != 0:
            self.move_single_axis(dx, 0)
        if dy != 0:
            self.move_single_axis(0, dy)

    def move_single_axis(self, dx, dy):
        # Move the rect
        self.rect.x += dx
        self.rect.y += dy

        # If you collide with a wall, move out based on velocity
        collide = False
        for wall in self.game.walls:
            if self.rect.colliderect(wall.rect):
                collide = True
                if dx > 0:  # Moving right; Hit the left side of the wall
                    self.rect.right = wall.rect.left
                if dx < 0:  # Moving left; Hit the right side of the wall
                    self.rect.left = wall.rect.right
                if dy > 0:  # Moving down; Hit the top side of the wall, lose velocity if just landed
                    self.rect.bottom = wall.rect.top
                    if self.jumping:
                        self.velocity.y = 0
                        self.jumping = False
                if dy < 0:  # Moving up; Hit the bottom side of the wall, lose velocity
                    self.rect.top = wall.rect.bottom
                    self.velocity.y = 0
        if not collide:
            self.jumping = True

    def apply_force(self, force_direction, force_magnitude):
        x = math.sin(self.velocity.x) * self.velocity.y + math.sin(force_direction) * force_magnitude
        y = math.cos(self.velocity.x) * self.velocity.y + math.cos(force_direction) * force_magnitude
        self.velocity.x = 0.5 * math.pi - math.atan2(y, x)
        self.velocity.y = math.hypot(x, y)

    def jump(self):
        # jump only if standing on a platform
        self.rect.y += 2
        hits = pygame.sprite.spritecollide(self, self.game.walls, False)
        self.rect.y -= 2
        if hits and not self.jumping:
            self.apply_force(settings.UP, settings.PLAYER_JUMP)
            self.jumping = True

    def jump_cut(self):
        if self.jumping:
            self.apply_force(settings.DOWN, 7 * settings.GRAVITY_MAGNITUDE)

    def update(self):
        # apply player movement
        if self.jumping:
            acceleration = 0.2 * settings.PLAYER_ACCELERATION
        else:
            acceleration = settings.PLAYER_ACCELERATION

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.apply_force(settings.LEFT, acceleration)
        if keys[pygame.K_RIGHT]:
            self.apply_force(settings.RIGHT, acceleration)

        # apply gravity
        self.apply_force(settings.DOWN, settings.GRAVITY_MAGNITUDE)

        # make sure player isn't moving too fast
        if self.velocity.y > settings.MAX_VELOCITY:
            self.velocity.y = settings.MAX_VELOCITY

        # calculate change in position to check for collisions while moving
        dx = math.sin(self.velocity.x) * self.velocity.y
        dy = math.cos(self.velocity.x) * self.velocity.y
        self.move(dx, dy)

















