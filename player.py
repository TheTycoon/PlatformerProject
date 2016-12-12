import pygame
import settings


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((settings.PLAYER_WIDTH, settings.PLAYER_HEIGHT))
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
        self.can_teleport = True

        # movement flags
        self.double_jumping = False
        self.wall_grabbing = False
        self.wall_jumping = False
        self.sprinting = False
        self.teleporting = False

        # attributes of the player
        self.max_energy = 20
        self.current_energy = 20
        self.energy_regen = settings.ENERGY_REGEN
        self.cooling_down = False
        self.cool_down = settings.ENERGY_COOLDOWN
        self.last = pygame.time.get_ticks()

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

        # Collisions are different for different kinds of blocks
        for block in self.game.blocks:
            if self.rect.colliderect(block.rect):
                if block.death is True:
                    self.game.restart_level()
                if block.name == 'wall':
                    self.wall_collide(block, dx, dy)
                elif block.name == 'platform':
                    self.platform_collide(block, dy)
                elif block.name == 'bounce':
                    self.bounce_collide(block, dx, dy)

        self.position.x = self.rect.x
        self.position.y = self.rect.y

        # this is currently placeholder for gaining abilities
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

    def landing_reset(self, velocity=0):
        self.velocity.y = velocity
        self.double_jumping = False
        self.wall_jumping = False
        self.teleporting = False

    def wall_collide(self, block, dx, dy):
        if dx > 0:  # Moving right; Hit the left side of the wall
            self.rect.right = block.rect.left

        if dx < 0:  # Moving left; Hit the right side of the wall
            self.rect.left = block.rect.right

        # Moving down; Hit the top side of the wall
        # Extra Behaviors:
        # - Resets the ability to double jump
        # - Resets the ability to air dash
        if dy > 0:
            self.rect.bottom = block.rect.top
            self.landing_reset()

        # Moving up; Hit the bottom side of the wall, lose velocity
        if dy < 0:
            self.rect.top = block.rect.bottom
            self.velocity.y = 0

    def platform_collide(self, block, dy):
        # moving down when colliding
        if dy > 0:
            self.rect.bottom = block.rect.top
            self.landing_reset()

    def bounce_collide(self, block, dx, dy):
        if dy > 0:

            self.rect.bottom = block.rect.top

            if block.direction == 'up':
                self.landing_reset(self.velocity.y)
                self.velocity.y *= -1
                self.velocity.y -= block.bounce
            else:
                self.landing_reset()
        if dy < 0:
            self.rect.top = block.rect.bottom
            if block.direction == 'down':
                self.velocity.y *= -1
                self.velocity.y += block.bounce
        if dx > 0:
            self.rect.right = block.rect.left
            if block.direction == 'left':
                self.velocity.x *= -1
                self.velocity.x -= block.bounce
        if dx < 0:
            self.rect.left = block.rect.right
            if block.direction == 'right':
                self.velocity.x *= -1
                self.velocity.x += block.bounce

    def jump(self):
        # jump only if standing on a platform
        if not self.check_airborne():
            self.velocity.y = - settings.PLAYER_JUMP

    def double_jump(self):
        if self.check_airborne() and not self.double_jumping:
            self.double_jumping = True
            self.velocity.y = -settings.PLAYER_JUMP

    def wall_jump(self):
        self.wall_jumping = True
        self.wall_grabbing = False
        self.velocity.y = -3 * settings.PLAYER_JUMP

    def jump_cut(self):
        if self.check_airborne():
            if self.velocity.y < -1:
                self.velocity.y = -1

    def platform_drop(self):
        if self.check_platform():
            self.rect.y += settings.PLAYER_HEIGHT
            self.velocity.y = settings.PLAYER_JUMP / 2.5

    def check_platform(self):
        hits = False
        self.rect.y += 1
        for platform in self.game.platforms:
            if self.rect.bottom >= platform.rect.top and self.rect.top < platform.rect.top:
                if self.rect.colliderect(platform):
                    hits = True
        self.rect.y -= 1

        if hits:
            return True
        else:
            return False

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

    def check_wall(self, direction):

        if direction == 'left':
            check = -1
        elif direction == 'right':
            check = 1
        else:
            check = 0

        self.rect.x += check
        hits= pygame.sprite.spritecollide(self, self.game.walls, False)
        self.rect.x -= check

        if hits:
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
            if self.wall_jumping:
                stop_movement = False

        if not stop_movement:
            self.move(dx, dy)

    def begin_frame(self):
        # Regain the standard amount of energy per frame if not on cooldown, set initial accelerations for new frame
        if self.current_energy <= 0 and not self.cooling_down:
            self.cooling_down = True
            self.last = pygame.time.get_ticks()

        now = pygame.time.get_ticks()
        if self.cooling_down and now - self.last >= self.cool_down:
            self.last = now
            self.cooling_down = False

        if not self.cooling_down:
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
        # If airborne, player accelerates at only 20% of normal value, gives almost no air control
        if self.check_airborne():
            acceleration = 0.2 * settings.PLAYER_ACCELERATION
        else:
            acceleration = settings.PLAYER_ACCELERATION

        if self.game.joystick.get_axis(settings.JOYAXIS['LeftHorizontal']) < -0.85:
            self.acceleration.x = - acceleration
        if self.game.joystick.get_axis(settings.JOYAXIS['LeftHorizontal']) > 0.85:
            self.acceleration.x = acceleration

    def joystick_sprint(self):
        if self.current_energy >= 2:
            if self.game.joystick.get_axis(settings.JOYAXIS['Trigger']) < -0.85:
                self.current_energy -= 2
                if self.current_energy <= 0:
                    self.current_energy = 0
                self.acceleration.x *= 3
                return True
        return False

    def joystick_wall_grab(self):
        if self.check_wall('left') and self.game.joystick.get_axis(settings.JOYAXIS['LeftHorizontal']) < -0.85:
            self.wall_grabbing = True
        elif self.check_wall('right') and self.game.joystick.get_axis(settings.JOYAXIS['LeftHorizontal']) > 0.85:
            self.wall_grabbing = True
        else:
            self.wall_grabbing = False

        if self.wall_grabbing is True:
            if self.current_energy >= 2:
                self.acceleration = pygame.math.Vector2(0, 0)
                self.velocity = pygame.math.Vector2(0, 0)
                self.current_energy -= 2
                self.move(0, 0)
                self.double_jumping = False
                return True
        return False

    def joystick_teleport(self, direction):
        if direction == 'left':
            teleport = - settings.TELEPORT_MAGNITUDE
        elif direction == 'right':
            teleport = settings.TELEPORT_MAGNITUDE
        else:
            teleport = 0
        if self.current_energy >= self.max_energy / 2:
            self.current_energy = 0
            self.teleporting = True
            self.move(teleport, 0)

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





















