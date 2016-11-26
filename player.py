import pygame
import settings


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
        self.position = pygame.math.Vector2(self.x, self.y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)

        self.airborne = False
        self.double_jumping = False

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
        for wall in self.game.walls:
            if self.rect.colliderect(wall.rect):

                # check for a death block first / add more here
                # animation for death, message, game over screen, restart level, etc
                if wall.death is True:
                    self.kill()
                    print("You Died!")


                if dx > 0:  # Moving right; Hit the left side of the wall
                    self.rect.right = wall.rect.left
                if dx < 0:  # Moving left; Hit the right side of the wall
                    self.rect.left = wall.rect.right

                # Moving down and landing on top of a wall has extra behaviors
                # Resets the ability to double jump
                # Checks if it is a bounce block
                if dy > 0:                                  # Moving down; Hit the top side of the wall
                    self.rect.bottom = wall.rect.top
                    self.double_jumping = False
                    if wall.bounce > 0:
                        self.velocity.y = - wall.bounce
                    else:
                        self.velocity.y = 0

                if dy < 0:  # Moving up; Hit the bottom side of the wall, lose velocity
                    self.rect.top = wall.rect.bottom
                    self.velocity.y = 0

    def jump(self):
        # jump only if standing on a platform
        if not self.check_airborne() and not self.airborne:
            self.airborne = True
            self.velocity.y = -settings.PLAYER_JUMP

    def double_jump(self):
        if self.check_airborne() and not self.double_jumping:
            self.double_jumping = True
            self.velocity.y = -settings.PLAYER_JUMP

    def jump_cut(self):
        if self.airborne:
            if self.velocity.y < -1:
                self.velocity.y = -1

    def check_airborne(self):
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, self.game.walls, False)
        self.rect.y -= 1
        if hits:
            return False
        else:
            return True

    def get_block_friction(self):
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, self.game.walls, False)
        self.rect.y -= 1
        if hits:
            return hits[0].friction
        else:
            return None

    def update(self):
        # This first airborne check resets the flag and initial acceleration
        # for the current frame
        if self.check_airborne():
            self.airborne = True
            self.acceleration = pygame.math.Vector2(0, settings.GRAVITY_MAGNITUDE)
        else:
            self.airborne = False
            self.acceleration = pygame.math.Vector2(0, 0)

        # Implement any other real-time player movement here
        # airborne controls are diminished
        if self.airborne:
            acceleration = 0.2 * settings.PLAYER_ACCELERATION
        else:
            acceleration = settings.PLAYER_ACCELERATION
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acceleration.x = -acceleration
        if keys[pygame.K_RIGHT]:
            self.acceleration.x = acceleration

        # apply drag if airborne, friction only to x direction if walking
        if self.airborne:
            self.acceleration *= settings.DRAG
        else:
            friction = self.get_block_friction()
            self.acceleration.x += self.velocity.x * friction

        # equations of motion
        self.velocity += self.acceleration
        if abs(self.velocity.x) < 0.1:
            self.velocity.x = 0
        if self.velocity.y > settings.MAX_FALL_VELOCITY:
            self.velocity.y = settings.MAX_FALL_VELOCITY
        elif self.velocity.y < - settings.MAX_JUMP_VELOCITY:
            self.velocity.y = - settings.MAX_JUMP_VELOCITY

        new_position = self.position + self.velocity + 0.5 * self.acceleration
        dx = new_position.x - self.position.x
        dy = new_position.y - self.position.y

        self.move(dx, dy)


















