import pygame
import settings
import sprites


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
        self.rect = self.image.get_rect()
        self.hit_image = pygame.Surface((24, 63))
        self.hit_rect = pygame.Rect(0, 0, 24, 63)
        self.hit_image.fill(settings.WHITE, self.hit_rect)
        self.hit_image.set_alpha(100)

        # animation stuff
        self.current_frame = 0
        self.last_update = 0
        self.facing_right = True

        # ability flags
        self.can_double_jump = True
        self.can_wall_grab = True
        self.can_sprint = True
        self.can_teleport = True

        # movement flags
        self.walking = False
        self.jumping = False
        self.double_jumping = False
        self.wall_grabbing = False
        self.wall_jumping = False
        self.sprinting = False
        self.teleporting = False

        self.sword_attacking = False
        self.thrust_attacking = False
        self.ranged_attacking = False

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

        self.jumping_frames_right = []
        for i in range(8):
            self.jumping_frames_right.append(self.game.jump_spritesheet.get_image(223 * i, 0, 223, 342))
        self.jumping_frames_left = []
        for frame in self.jumping_frames_right:
            frame.set_colorkey(settings.BLACK)
            self.jumping_frames_left.append(pygame.transform.flip(frame, True, False))

        self.double_jumping_frames_right = []
        for i in range(8):
            self.double_jumping_frames_right.append(self.game.double_jump_spritesheet.get_image(286 * i, 0, 286, 287))
        self.double_jumping_frames_left = []
        for frame in self.double_jumping_frames_right:
            frame.set_colorkey(settings.BLACK)
            self.double_jumping_frames_left.append(pygame.transform.flip(frame, True, False))

        self.wall_slide_frames_right = []
        for i in range(4):
            self.wall_slide_frames_right.append(self.game.wall_slide_spritesheet.get_image(206 * i, 0, 206, 300))
        self.wall_slide_frames_left = []
        for frame in self.wall_slide_frames_right:
            frame.set_colorkey(settings.BLACK)
            self.wall_slide_frames_left.append(pygame.transform.flip(frame, True, False))

        self.sword_attack_frames_right = []
        for i in range(8):
            self.sword_attack_frames_right.append(self.game.sword_attack_spritesheet.get_image(512 * i, 0, 512, 405))
        self.sword_attack_frames_left = []
        for frame in self.sword_attack_frames_right:
            frame.set_colorkey(settings.BLACK)
            self.sword_attack_frames_left.append(pygame.transform.flip(frame, True, False))

        self.thrust_attack_frames_right = []
        for i in range(8):
            self.thrust_attack_frames_right.append(self.game.sword_thrust_spritesheet.get_image(536 * i, 0, 536, 265))
        self.thrust_attack_frames_left = []
        for frame in self.thrust_attack_frames_right:
            frame.set_colorkey(settings.BLACK)
            self.thrust_attack_frames_left.append(pygame.transform.flip(frame, True, False))

        self.ranged_attack_frames_right = []
        for i in range(8):
            self.ranged_attack_frames_right.append(self.game.ranged_attack_spritesheet.get_image(279 * i, 0, 279, 276))
        self.ranged_attack_frames_left = []
        for frame in self.ranged_attack_frames_right:
            frame.set_colorkey(settings.BLACK)
            self.ranged_attack_frames_left.append(pygame.transform.flip(frame, True, False))

        self.bullet_frames = []
        for i in range(8):
            self.bullet_frames.append(self.game.red_bullet_spritesheet.get_image(60 * i, 0, 60, 61))
        # for frame in self.bullet_frames:
        #     frame.set_colorkey(settings.BLACK)

        self.teleporting_frames = []
        for i in range(8):
            self.teleporting_frames.append(self.game.teleport_spritesheet.get_image(185 * i, 0, 185, 198))
        for frame in self.teleporting_frames:
            frame.set_colorkey(settings.BLACK)

    def animate(self):
        now = pygame.time.get_ticks()

        if self.sword_attacking:
            if now - self.last_update > 50:
                self.last_update = now
                if self.facing_right:
                    self.image = self.sword_attack_frames_right[self.current_frame]
                    self.current_frame = self.current_frame + 1
                else:
                    self.image = self.sword_attack_frames_left[self.current_frame]
                    self.current_frame = self.current_frame + 1


        if self.thrust_attacking:
            if now - self.last_update > 50:
                self.last_update = now
                if self.facing_right:
                    self.image = self.thrust_attack_frames_right[self.current_frame]
                    self.current_frame += 1
                else:
                    self.image = self.thrust_attack_frames_left[self.current_frame]
                    self.current_frame += 1
            if self.current_frame == len(self.thrust_attack_frames_right):
                self.thrust_attacking = False
                self.current_frame = 4


        if self.ranged_attacking:
            if now - self.last_update > 20:
                self.last_update = now
                if self.facing_right:
                    self.image = self.ranged_attack_frames_right[self.current_frame]
                    self.current_frame += 1
                else:
                    self.image = self.ranged_attack_frames_left[self.current_frame]
                    self.current_frame += 1
            if self.current_frame == len(self.ranged_attack_frames_right):
                self.ranged_attacking = False
                self.current_frame = 0


        if not self.check_airborne():
            if self.velocity.x > 0:
                if self.sprinting:
                    if now - self.last_update > 50:
                        self.last_update = now
                        self.image = self.running_frames_right[self.current_frame]
                        self.current_frame = (self.current_frame + 1) % len(self.running_frames_right)
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
                if now - self.last_update > 150:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.standing_frames_right)
                    self.image = self.standing_frames_right[self.current_frame]
            elif self.velocity.x == 0 and not self.facing_right:
                if now - self.last_update > 150:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.standing_frames_left)
                    self.image = self.standing_frames_left[self.current_frame]

        elif self.wall_grabbing:
            if now - self.last_update > 100:
                self.last_update = now
                if self.check_wall('right'):
                    self.current_frame = (self.current_frame + 1) % len(self.wall_slide_frames_left)
                    self.image = self.wall_slide_frames_left[self.current_frame]
                elif self.check_wall('left'):
                    self.current_frame = (self.current_frame + 1) % len(self.wall_slide_frames_right)
                    self.image = self.wall_slide_frames_right[self.current_frame]


        elif self.double_jumping:
            if now - self.last_update > 25:
                self.last_update = now
                if self.facing_right:
                    self.current_frame = (self.current_frame + 1) % len(self.double_jumping_frames_right)
                    self.image = self.double_jumping_frames_right[self.current_frame]
                else:
                    self.current_frame = (self.current_frame + 1) % len(self.double_jumping_frames_left)
                    self.image = self.double_jumping_frames_left[self.current_frame]

        elif self.jumping:
            if now - self.last_update > 100:
                self.last_update = now
                if self.facing_right:
                    self.current_frame = (self.current_frame + 1) % len(self.jumping_frames_right)
                    self.image = self.jumping_frames_right[self.current_frame]
                else:
                    self.current_frame = (self.current_frame + 1) % len(self.jumping_frames_left)
                    self.image = self.jumping_frames_left[self.current_frame]

        else:
            if now - self.last_update > 100:
                self.current_frame = 0
                if self.facing_right:
                    self.image = self.standing_frames_right[self.current_frame]
                else:
                    self.image = self.standing_frames_left[self.current_frame]



    # this is pretty ugly, but I don't know of a better way to go about fixing the animations
    def animation_offset(self):
        if self.wall_grabbing:
            self.rect.y = self.hit_rect.y
            if self.check_wall('right'):
                self.rect.x = self.hit_rect.x - 20
            elif self.check_wall('left'):
                self.rect.x = self.hit_rect.x - 5

        if self.facing_right and not self.wall_grabbing and not self.thrust_attacking:
            self.rect.x = self.hit_rect.x - 12
            self.rect.y = self.hit_rect.y
            if self.jumping:
                self.rect.y = self.hit_rect.y - 20
            if self.double_jumping:
                self.rect.x = self.hit_rect.x - 24
                self.rect.y = self.hit_rect.y - 5
        elif not self.facing_right and not self.wall_grabbing and not self.thrust_attacking:
            self.rect.x = self.hit_rect.x - 12
            self.rect.y = self.hit_rect.y
            if not self.check_wall('left'):
                if self.walking:
                    self.rect.x = self.hit_rect.x - 24
                if self.sprinting:
                    self.rect.x = self.hit_rect.x - 42
            if self.jumping:
                self.rect.x = self.hit_rect.x - 20
                self.rect.y = self.hit_rect.y - 5
            if self.double_jumping:
                self.rect.y = self.hit_rect.y - 10

        if self.thrust_attacking:
            self.rect.x = self.hit_rect.x -50


        if self.facing_right and self.sword_attacking:
            self.rect.x = self.hit_rect.x - 45
            self.rect.y = self.hit_rect.y - 25

    def move(self, dx, dy):
        # Move each axis separately. Note that this checks for collisions both times.
        if dx != 0:
            self.move_single_axis(dx, 0)
        if dy != 0:
            self.move_single_axis(0, dy)

    def move_single_axis(self, dx, dy):
        # Move the rect
        self.hit_rect.x += dx
        self.hit_rect.y += dy

        # Collisions are different for different kinds of blocks
        for block in self.game.blocks:
            if self.hit_rect.colliderect(block.rect):
                if block.death is True:
                    self.game.restart_level()
                if block.name == 'wall' or block.name == 'ice':
                    self.wall_collide(block, dx, dy)
                elif block.name == 'platform':
                    self.platform_collide(block, dy)
                elif block.name == 'bounce':
                    self.bounce_collide(block, dx, dy)

        self.position.x = self.hit_rect.x
        self.position.y = self.hit_rect.y

        # this is currently placeholder for gaining abilities
        for block in self.game.abilities:
            if self.hit_rect.colliderect(block.rect):
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

    def landing_reset(self):
        if self.facing_right:
            self.image = self.standing_frames_right[0]
        else:
            self.image = self.standing_frames_left[0]

        self.velocity.y = 0
        self.jumping = False
        self.double_jumping = False
        self.wall_grabbing = False
        self.wall_jumping = False

    def wall_collide(self, block, dx, dy):
        if dx > 0:  # Moving right; Hit the left side of the wall, lose horizontal velocity
            self.hit_rect.right = block.rect.left
            self.velocity.x = 0

        if dx < 0:  # Moving left; Hit the right side of the wall, lose horizontal velocity
            self.hit_rect.left = block.rect.right
            self.velocity.x = 0

        if dy > 0:  # Moving down; Hit the top side of the wall, reset abilities and vertical velocity
            self.hit_rect.bottom = block.rect.top
            self.landing_reset()


        if dy < 0:  # Moving up; Hit the bottom side of the wall, lose velocity
            self.hit_rect.top = block.rect.bottom
            self.velocity.y = 0

    def platform_collide(self, block, dy):
        # moving down when colliding
        if dy > 0:
            self.hit_rect.bottom = block.rect.top
            self.landing_reset()

    def bounce_collide(self, block, dx, dy):
        if dy > 0:
            self.hit_rect.bottom = block.rect.top
            if block.direction == 'up':
                self.jumping = True
                self.double_jumping = False
                self.wall_jumping = False
                self.velocity.y *= -1
                self.velocity.y -= block.bounce
            else:
                self.landing_reset()
        if dy < 0:
            self.hit_rect.top = block.rect.bottom
            if block.direction == 'down':
                self.velocity.y *= -1
                self.velocity.y += block.bounce
        if dx > 0:
            self.hit_rect.right = block.rect.left
            if block.direction == 'left':
                self.velocity.x *= -1
                self.velocity.x -= block.bounce
        if dx < 0:
            self.hit_rect.left = block.rect.right
            if block.direction == 'right':
                self.velocity.x *= -1
                self.velocity.x += block.bounce

    def jump(self):
        # jump only if standing on a platform
        if not self.check_airborne():
            self.velocity.y = - settings.PLAYER_JUMP
            self.jumping = True

    def double_jump(self):
        if self.check_airborne() and not self.double_jumping:
            self.double_jumping = True
            self.velocity.y = -settings.PLAYER_JUMP

    def wall_jump(self):
        self.wall_jumping = True
        self.wall_grabbing = False
        if self.facing_right:
            self.velocity.x = -1 * settings.PLAYER_JUMP
        else:
            self.velocity.x = settings.PLAYER_JUMP
        self.velocity.y = -2 * settings.PLAYER_JUMP - settings.GRAVITY_MAGNITUDE

    def jump_cut(self):
        if self.check_airborne():
            if self.velocity.y < 0:
                self.velocity.y = 0

    def platform_drop(self):
        if self.check_platform():
            self.hit_rect.y += settings.PLAYER_HEIGHT
            self.velocity.y = settings.PLAYER_JUMP / 2.5

    def check_platform(self):
        hits = False
        self.hit_rect.y += 1
        for platform in self.game.platforms:
            if self.hit_rect.bottom >= platform.rect.top and self.hit_rect.top < platform.rect.top:
                if self.hit_rect.colliderect(platform):
                    hits = True
        self.hit_rect.y -= 1

        if hits:
            return True
        else:
            return False

    def check_airborne(self):
        self.hit_rect.y += 1
        hits = False
        for block in self.game.blocks:
            if self.hit_rect.colliderect(block):
                hits = True
        self.hit_rect.y -= 1
        if hits:
            return False
        else:
            return True

    def get_block_friction(self):
        self.hit_rect.y += 1
        hits = False
        for block in self.game.blocks:
            if self.hit_rect.colliderect(block):
                hits = True
                friction = block.friction
        self.hit_rect.y -= 1
        if hits:
            return friction
        else:
            return 0

    def check_wall(self, direction):

        if direction == 'left':
            check = -1
        elif direction == 'right':
            check = 1
        else:
            check = 0

        self.hit_rect.x += check
        hits = False
        for wall in self.game.walls:
            if self.hit_rect.colliderect(wall):
                hits = True
        self.hit_rect.x -= check

        if hits:
            return True
        else:
            return False

    def update(self):
        self.regain_energy()
        self.animate()
        self.animation_offset()
        if self.current_frame == len(self.sword_attack_frames_right) and self.sword_attacking:
            self.sword_attacking = False
            self.current_frame = 0

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

        if self.ranged_attacking and not self.check_airborne():
            dx = 0

        if self.check_airborne():
            if self.can_wall_grab and self.joystick_wall_grab():
                stop_movement = True
            if self.wall_jumping:
                stop_movement = False

        if not stop_movement:
            self.move(dx, dy)

    def begin_frame(self):
        if -0.85 < self.game.joystick.get_axis(settings.JOYAXIS['LeftHorizontal']) < 0.85 or self.check_airborne():
            self.walking = False
            self.wall_grabbing = False

        if -0.85 < self.game.joystick.get_axis(settings.JOYAXIS['Trigger']) <= 0  or self.current_energy < 2:
            self.sprinting = False

        if self.check_airborne():
            self.acceleration = pygame.math.Vector2(0, settings.GRAVITY_MAGNITUDE)
        else:
            self.acceleration = pygame.math.Vector2(0, 0)



    def regain_energy(self):
        # Regain the standard amount of energy per frame if not on cooldown, set initial accelerations for new frame
        if self.current_energy <= 0 and not self.cooling_down:
            self.cooling_down = True
            self.last = pygame.time.get_ticks()

        now = pygame.time.get_ticks()
        if self.cooling_down and now - self.last >= self.energy_cooldown:
            self.last = now
            self.cooling_down = False

        if not self.cooling_down:
            self.current_energy += self.energy_regen
            if self.current_energy > self.max_energy:
                self.current_energy = self.max_energy

    def joystick_movement(self):
        # If airborne, player accelerates at only 20% of normal value, gives almost no air control
        if self.check_airborne():
            acceleration = 0.2 * settings.PLAYER_ACCELERATION
            airborne = True
        else:
            acceleration = settings.PLAYER_ACCELERATION
            airborne = False


        if self.game.joystick.get_axis(settings.JOYAXIS['LeftHorizontal']) < -0.85:
            self.acceleration.x = - acceleration
            self.facing_right = False
            if not airborne:
                self.walking = True
        if self.game.joystick.get_axis(settings.JOYAXIS['LeftHorizontal']) > 0.85:
            self.acceleration.x = acceleration
            self.facing_right = True
            if not airborne:
                self.walking = True

    def joystick_sprint(self):
        if self.current_energy >= 5:
            if self.game.joystick.get_axis(settings.JOYAXIS['Trigger']) < -0.85 and \
                    (self.game.joystick.get_axis(settings.JOYAXIS['LeftHorizontal']) > 0.85 or \
                     self.game.joystick.get_axis(settings.JOYAXIS['LeftHorizontal']) < -0.85):
                self.current_energy -= 5
                if self.current_energy <= 0:
                    self.current_energy = 0
                self.acceleration.x *= 3
                self.sprinting = True
                return True
        return False

    def joystick_wall_grab(self):
        if self.check_wall('left') and self.game.joystick.get_axis(settings.JOYAXIS['Trigger']) > 0.85:
            self.wall_grabbing = True
        elif self.check_wall('right') and self.game.joystick.get_axis(settings.JOYAXIS['Trigger']) > 0.85:
            self.wall_grabbing = True
        else:
            self.wall_grabbing = False

        if self.wall_grabbing is True:
            if self.current_energy >= 5:
                self.acceleration = pygame.math.Vector2(0, 0)
                self.velocity = pygame.math.Vector2(0, 0)
                self.current_energy -= 5
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
            teleport_animation = sprites.SingleAnimation(self.rect.center, self.teleporting_frames, 10)
            self.game.all_sprites.add(teleport_animation)
            self.move(teleport, 0)

    def sword_attack(self):
        self.current_frame = 0
        self.sword_attacking = True

    def thrust_attack(self):
        self.current_frame = 0
        self.thrust_attacking = True

    def ranged_attack(self):
        if self.current_energy >= 20:
            self.current_energy -= 20
            self.current_frame = 0
            self.ranged_attacking = True
            direction = None
            if self.facing_right:
                direction = 'right'
            else:
                direction= 'left'
            bullet = sprites.Bullet(self.game, self.bullet_frames, 100, self.hit_rect.center, direction)
            self.game.all_sprites.add(bullet)
            self.game.bullets.add(bullet)



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





















