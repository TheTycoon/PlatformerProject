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
        self.rect.topleft = (x, y)
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)

        # ability flags
        self.can_double_jump = False
        self.can_wall_grab = False
        self.can_dash = False
        self.can_air_dash = False

        # movement flags
        self.double_jumping = False
        self.wall_grabbing = False

        # attributes of the player
        self.max_energy = 100
        self.current_energy = 100
        self.energy_regen = settings.ENERGY_REGEN

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

        for block in self.game.abilities:
            if self.rect.colliderect(block.rect):
                if block.name == 'double_jump':
                    self.can_double_jump = True
                    block.kill()
                    print("You Gained Double Jump!")
                if block.name == 'wall_grab':
                    self.can_wall_grab = True
                    block.kill()
                    print("You Gained Wall Grab!")

        # If you collide with a wall, move out based on velocity
        for block in self.game.blocks:
            if self.rect.colliderect(block.rect):

                # check for a death block first / add more here
                # animation for death, message, game over screen, restart level, etc
                if block.death is True:
                    self.kill()
                    print("You Died!")


                if dx > 0:  # Moving right; Hit the left side of the wall
                    self.rect.right = block.rect.left

                if dx < 0:  # Moving left; Hit the right side of the wall
                    self.rect.left = block.rect.right

                # Moving down; Hit the top side of the wall
                # Extra Behaviors:
                # - Resets the ability to double jump
                # - Applies bounce if applicable
                if dy > 0:
                    self.rect.bottom = block.rect.top
                    self.double_jumping = False
                    if block.bounce > 0:
                        self.velocity.y = - block.bounce
                    else:
                        self.velocity.y = 0
                # Moving up; Hit the bottom side of the wall, lose velocity
                if dy < 0:
                    self.rect.top = block.rect.bottom
                    self.velocity.y = 0

    def jump(self):
        # jump only if standing on a platform
        if not self.check_airborne():
            self.velocity.y = - settings.PLAYER_JUMP

    def double_jump(self):
        if self.check_airborne() and not self.double_jumping:
            self.double_jumping = True
            self.velocity.y = -settings.PLAYER_JUMP

    def jump_cut(self):
        if self.check_airborne():
            if self.velocity.y < -1:
                self.velocity.y = -1

    def check_airborne(self):
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        self.rect.y -= 1
        if hits:
            return False
        else:
            return True

    def get_block_friction(self):
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        self.rect.y -= 1
        if hits:
            return hits[0].friction
        else:
            return 0

    def check_wall_grab(self):
        if self.can_wall_grab:
            self.rect.x += 1
            hits_right = pygame.sprite.spritecollide(self, self.game.blocks, False)
            self.rect.x -= 1

            self.rect.x -= 1
            hits_left = pygame.sprite.spritecollide(self, self.game.blocks, False)
            self.rect.x += 1

            if hits_right or hits_left:
                return True
            else:
                return False
        else:
            return False

    def update(self):
        # Regain Energy Every Frame
        self.current_energy += self.energy_regen
        if self.current_energy > self.max_energy:
            self.current_energy = self.max_energy

        # This first airborne check sets initial acceleration for current frame
        if self.check_airborne():
            self.acceleration = pygame.math.Vector2(0, settings.GRAVITY_MAGNITUDE)
        else:
            self.acceleration = pygame.math.Vector2(0, 0)

        # Real-time Player Controls:

        # - airborne LEFT/RIGHT controls are diminished
        if self.check_airborne():
            acceleration = 0.2 * settings.PLAYER_ACCELERATION
        else:
            acceleration = settings.PLAYER_ACCELERATION

        # keyboard controls for left/right
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acceleration.x = -acceleration
        if keys[pygame.K_RIGHT]:
            self.acceleration.x = acceleration

        # joystick controls for left/right
        if self.game.joystick.get_axis(0) < -0.85:
            self.acceleration.x = - acceleration
        if self.game.joystick.get_axis(0) > 0.85:
            self.acceleration.x = acceleration

        # Apply resistance depending on block friction or air drag
        if self.check_airborne():
            self.acceleration *= settings.DRAG
        else:
            friction = self.get_block_friction()
            self.acceleration.x += self.velocity.x * friction

        # CALCULATE FINAL RESULTS AND SMOOTH/LIMIT THEM BEFORE CHECKING COLLISIONS
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

        # WALL GRAB - RESTRICTS MOVEMENT - NEEDS TO BE ABSOLUTELY LAST
        if self.game.joystick.get_axis(settings.JOYSTICK['LeftTrigger']) > 0.85 and self.check_wall_grab():
            if self.current_energy >= 1:
                self.move(0, 0)
                self.acceleration = pygame.math.Vector2(0, 0)
                self.velocity = pygame.math.Vector2(0, 0)
                self.current_energy -= 1
                if self.current_energy < 0:
                    self.current_energy = 0
            else:
                self.move(dx, dy)
        else:
            self.move(dx, dy)


















