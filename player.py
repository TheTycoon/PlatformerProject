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
        self.can_double_jump = True
        self.can_wall_grab = True
        self.can_sprint = True
        self.can_air_dash = True

        # movement flags
        self.double_jumping = False
        self.wall_grabbing = False
        self.sprinting = False
        self.air_dashing = False

        # attributes of the player
        self.max_energy = 20
        self.current_energy = 20
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
                if block.name == 'sprint':
                    self.can_sprint = True
                    block.kill()
                    print("You Gained Sprint!")

        # If you collide with a wall, move out based on velocity
        for block in self.game.blocks:
            if self.rect.colliderect(block.rect):

                # check for a death block first / add more here
                # animation for death, message, game over screen, restart level, etc
                if block.death is True:
                    self.game.restart_level()
                    print("You Died!")

                if dx > 0:  # Moving right; Hit the left side of the wall
                    self.rect.right = block.rect.left

                if dx < 0:  # Moving left; Hit the right side of the wall
                    self.rect.left = block.rect.right

                # Moving down; Hit the top side of the wall
                # Extra Behaviors:
                # - Resets the ability to double jump
                # - Resets the ability to air dash
                # - Applies bounce if applicable
                if dy > 0:
                    self.rect.bottom = block.rect.top
                    self.double_jumping = False
                    self.air_dashing = False
                    if block.bounce > 0:
                        self.velocity.y *= -1
                        self.velocity.y += -block.bounce
                    else:
                        self.velocity.y = 0
                # Moving up; Hit the bottom side of the wall, lose velocity
                if dy < 0:
                    self.rect.top = block.rect.bottom
                    self.velocity.y = 0

        self.position.x = self.rect.x
        self.position.y = self.rect.y



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

    def check_wall(self):
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

    def update(self):
        self.begin_frame()
        self.joystick_movement()
        if self.can_sprint and not self.check_airborne():
            self.joystick_sprint()
        self.apply_resistance()
        self.calculate_velocity()

        new_position = self.position + self.velocity + 0.5 * self.acceleration
        dx = new_position.x - self.position.x
        dy = new_position.y - self.position.y

        # Final movement - Check All Abilities That Can Stop Regular Movement
        stop_movement = False
        if self.check_airborne():
            if self.can_wall_grab and self.joystick_wall_grab():
                stop_movement = True


        if not stop_movement:
            self.move(dx, dy)

    def begin_frame(self):
        # Regain the standard amount of energy per frame, set initial accelerations for new frame
        self.regain_energy()
        if self.check_airborne():
            self.acceleration = pygame.math.Vector2(0, settings.GRAVITY_MAGNITUDE)
        else:
            self.acceleration = pygame.math.Vector2(0, 0)

    def regain_energy(self):
        self.current_energy += self.energy_regen
        if self.current_energy > self.max_energy:
            self.current_energy = self.max_energy

    def joystick_movement(self):
        # If airborne, player acceleratess at only 20% of normal value, gives almost no air control
        if self.check_airborne():
            acceleration = 0.2 * settings.PLAYER_ACCELERATION
        else:
            acceleration = settings.PLAYER_ACCELERATION

        if self.game.joystick.get_axis(settings.JOYAXIS['LeftHorizontal']) < -0.85:
            self.acceleration.x = - acceleration
        if self.game.joystick.get_axis(settings.JOYAXIS['LeftHorizontal']) > 0.85:
            self.acceleration.x = acceleration

    def joystick_sprint(self):
        if self.current_energy >= 1:
            if self.game.joystick.get_axis(settings.JOYAXIS['RightTrigger']) > 0.85:
                self.current_energy -= 1
                self.acceleration.x *= 3
                return True
        return False

    # Need to clean this up a bit, maybe change the check wall method
    def joystick_wall_grab(self):
        if self.check_wall():
            if self.game.joystick.get_axis(settings.JOYAXIS['LeftHorizontal']) > 0.85 or \
               self.game.joystick.get_axis(settings.JOYAXIS['LeftHorizontal']) < -0.85:
                    if self.current_energy >= 1:
                        self.acceleration = pygame.math.Vector2(0, 0)
                        self.velocity = pygame.math.Vector2(0, 0)
                        self.current_energy -= 1
                        self.move(0, 0)
                        self.double_jumping = False
                        return True
        return False


    # this needs to cost a lot of energy or be reworked a bit
    def joystick_air_dash(self, direction):
        if direction == 'left':
            dash = - settings.AIR_DASH_MAGNITUDE
        if direction == 'right':
            dash = settings.AIR_DASH_MAGNITUDE
        if self.current_energy >= 10:
            self.current_energy -= 10
            self.air_dashing = True
            self.move(dash, 0)


    def apply_resistance(self):
        # Apply resistance depending on block friction or air drag
        if self.check_airborne():
            self.acceleration *= settings.DRAG
        else:
            friction = self.get_block_friction()
            self.acceleration.x += self.velocity.x * friction

    def calculate_velocity(self):
        self.velocity += self.acceleration
        if abs(self.velocity.x) < 0.1:
            self.velocity.x = 0
        if self.velocity.y > settings.MAX_FALL_VELOCITY:
            self.velocity.y = settings.MAX_FALL_VELOCITY
        elif self.velocity.y < - settings.MAX_JUMP_VELOCITY:
            self.velocity.y = - settings.MAX_JUMP_VELOCITY



    # NOT CURRENTLY SUPPORTING KEYBOARD CONTROLS
    # def keyboard_controls(self):
    #     # If airborne, player acceleratess at only 20% of normal value
    #     if self.check_airborne():
    #         acceleration = 0.2 * settings.PLAYER_ACCELERATION
    #     else:
    #         acceleration = settings.PLAYER_ACCELERATION
    #
    #     keys = pygame.key.get_pressed()
    #     if keys[pygame.K_LEFT] or keys[pygame.K_a]:
    #         self.acceleration.x = -acceleration
    #     if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
    #         self.acceleration.x = acceleration
    #
    # def keyboard_wall_grab(self):
    #     keys = pygame.key.get_pressed()
    #     if keys[pygame.K_RETURN] and self.check_wall():
    #         if self.current_energy >= 1:
    #             self.move(0, 0)
    #             self.acceleration = pygame.math.Vector2(0, 0)
    #             self.velocity = pygame.math.Vector2(0, 0)
    #             self.current_energy -= 1
    #             if self.current_energy < 0:
    #                 self.current_energy = 0
    #             return True
    #     return False




















