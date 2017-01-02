import pygame
import settings


class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pygame.image.load(filename).convert_alpha()

    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pygame.transform.scale(image, (width // 4, height // 4))
        return image


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.load_images()
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)

        # rect stuff
        self.image = self.standing_frames_right[0]
        self.rect = pygame.Rect(0, 0, 32, 64)
        self.rect.topleft = (x, y)
        self.collide_image = pygame.Surface((32, 64))
        self.hit_rect = pygame.Rect(0, 0, 32, 64)
        self.collide_image.fill(settings.WHITE, self.hit_rect)
        self.collide_image.set_alpha(100)

        # animation stuff
        self.current_frame = 0
        self.last_update = 0
        self.facing_left = False
        self.facing_right = False

        # ability flags
        self.can_double_jump = True
        self.can_wall_grab = False
        self.can_sprint = True
        self.can_teleport = False

        # movement flags
        self.walking = False
        self.jumping = False
        self.double_jumping = False
        self.wall_grabbing = False
        self.wall_jumping = False
        self.sprinting = False
        self.teleporting = False

        # attributes of the player / Currently Just Energy Attributes
        self.max_energy = settings.STARTING_ENERGY
        self.current_energy = settings.STARTING_ENERGY
        self.energy_regen = settings.ENERGY_REGEN
        self.energy_cooldown = settings.ENERGY_COOLDOWN
        self.cooling_down = False
        self.last = pygame.time.get_ticks()

    def load_images(self):
        self.standing_frames_right = []
        for i in range(8):
            self.standing_frames_right.append(self.game.idle_spritesheet.get_image(197 * i, 0, 197, 257))
        self.standing_frames_left = []
        for frame in self.standing_frames_right:
            frame.set_colorkey(settings.BLACK)
            self.standing_frames_left.append(pygame.transform.flip(frame, True, False))

        self.walking_frames_right = []
        for i in range(8):
            self.walking_frames_right.append(self.game.walk_spritesheet.get_image(240 * i, 0, 240, 258))
        self.walking_frames_left = []
        for frame in self.walking_frames_right:
            frame.set_colorkey(settings.BLACK)
            self.walking_frames_left.append(pygame.transform.flip(frame, True, False))

        self.running_frames_right = []
        for i in range(8):
            self.running_frames_right.append(self.game.run_spritesheet.get_image(313 * i, 0, 313, 260))
        self.running_frames_left = []
        for frame in self.running_frames_right:
            frame.set_colorkey(settings.BLACK)
            self.running_frames_left.append(pygame.transform.flip(frame, True, False))

    def animate(self):
        now = pygame.time.get_ticks()
        if self.velocity.x > 0:
            if self.sprinting:
                if now - self.last_update > 50:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.running_frames_right)
                    self.image = self.running_frames_right[self.current_frame]
            else:
                if now - self.last_update > 100:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.walking_frames_right)
                    self.image = self.walking_frames_right[self.current_frame]
        elif self.velocity.x < 0:
            if self.sprinting:
                if now - self.last_update > 50:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.running_frames_left)
                    self.image = self.running_frames_left[self.current_frame]
            else:
                if now - self.last_update > 100:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.walking_frames_left)
                    self.image = self.walking_frames_left[self.current_frame]
        elif self.velocity.x == 0 and self.facing_right:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames_right)
                self.image = self.standing_frames_right[self.current_frame]
        elif self.velocity.x == 0 and self.facing_left:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames_left)
                self.image = self.standing_frames_left[self.current_frame]

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
        if dx > 0:  # Moving right; Hit the left side of the wall, lose horizontal velocity
            self.rect.right = block.rect.left
            self.velocity.x = 0

        if dx < 0:  # Moving left; Hit the right side of the wall, lose horizontal velocity
            self.rect.left = block.rect.right
            self.velocity.x = 0

        if dy > 0:  # Moving down; Hit the top side of the wall, reset abilities and vertical velocity
            self.rect.bottom = block.rect.top
            self.landing_reset()


        if dy < 0:  # Moving up; Hit the bottom side of the wall, lose velocity
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
        self.animate()
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
        self.hit_rect.y = self.rect.y
        if self.facing_right:
            self.hit_rect.x = self.rect.x + 15
            if self.sprinting:
                self.hit_rect.x = self.rect.x + 45

        else:
            self.hit_rect.x = self.rect.x + 8



        # Regain the standard amount of energy per frame if not on cooldown, set initial accelerations for new frame
        if self.current_energy <= 0 and not self.cooling_down:
            self.cooling_down = True
            self.last = pygame.time.get_ticks()

        now = pygame.time.get_ticks()
        if self.cooling_down and now - self.last >= self.energy_cooldown:
            self.last = now
            self.cooling_down = False

        if not self.cooling_down:
            self.regain_energy()

        if self.check_airborne():
            self.acceleration = pygame.math.Vector2(0, settings.GRAVITY_MAGNITUDE)
        else:
            self.acceleration = pygame.math.Vector2(0, 0)

        if self.game.joystick.get_axis(settings.JOYAXIS['Trigger']) > -0.85 or self.current_energy < 2:
            self.sprinting = False

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
            self.facing_left = True
            self.facing_right = False
            self.walking = True
        if self.game.joystick.get_axis(settings.JOYAXIS['LeftHorizontal']) > 0.85:
            self.acceleration.x = acceleration
            self.facing_right = True
            self.facing_left = False
            self.walking = True

    def joystick_sprint(self):
        if self.current_energy >= 2:
            if self.game.joystick.get_axis(settings.JOYAXIS['Trigger']) < -0.85:
                self.current_energy -= 2
                if self.current_energy <= 0:
                    self.current_energy = 0
                self.acceleration.x *= 3
                self.sprinting = True
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





















