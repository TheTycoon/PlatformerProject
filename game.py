import pygame
from os import path
import settings
import player
import sprites
import tilemap


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.debug = False

        joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        if joysticks:
            self.joystick = joysticks[0]
            self.joystick.init()
            self.joystick_enabled = True
        else:
            self.joystick_enabled = False

        self.running = True
        self.load_data()

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.player_sprites = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.interactables = pygame.sprite.Group()
        self.abilities = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        self.levels = ['Map1.tmx', 'Map2.tmx', 'testmap.tmx']
        self.player = player.Player(self, 0, 0, )

        self.level_number = 0
        self.load_level(self.levels[self.level_number])

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(settings.FPS) / 1000.0
            self.clock.tick(settings.FPS)
            self.events()
            self.update()
            self.draw()

    def load_data(self):
        # Easy names for file directories
        self.game_folder = path.dirname(__file__)
        self.img_folder = path.join(self.game_folder, 'img')
        self.map_folder = path.join(self.game_folder, 'maps')

        self.idle_spritesheet = player.Spritesheet(path.join(self.img_folder, "player_idle.png"))
        self.walk_spritesheet = player.Spritesheet(path.join(self.img_folder, "player_walking.png"))
        self.run_spritesheet = player.Spritesheet(path.join(self.img_folder, "player_running.png"))
        self.jump_spritesheet = player.Spritesheet(path.join(self.img_folder, "player_jumping.png"))
        self.double_jump_spritesheet = player.Spritesheet(path.join(self.img_folder, "player_double_jumping.png"))
        self.wall_slide_spritesheet = player.Spritesheet(path.join(self.img_folder, "player_wall_slide.png"))
        self.sword_attack_spritesheet = player.Spritesheet(path.join(self.img_folder, "player_attack.png"))
        self.sword_thrust_spritesheet = player.Spritesheet(path.join(self.img_folder, "player_thrust.png"))
        self.teleport_spritesheet = player.Spritesheet(path.join(self.img_folder, "player_teleport.png"))
        self.ranged_attack_spritesheet = player.Spritesheet(path.join(self.img_folder, "player_ranged_attack.png"))
        self.red_bullet_spritesheet = player.Spritesheet(path.join(self.img_folder, "red_ball_bullet.png"))

        self.yellow_bullet_img = pygame.image.load(path.join(self.img_folder, "neon_yellow_ball.png")).convert_alpha()
        self.button_up_img = pygame.image.load(path.join(self.img_folder, "button_up.png")).convert_alpha()
        self.button_down_img = pygame.image.load(path.join(self.img_folder, "button_down.png")).convert_alpha()

    def load_level(self, mapname):
        self.map = tilemap.Map(path.join(self.map_folder, mapname))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.initialize_level()

    def initialize_level(self):
        for tile_object in self.map.tmxdata.objects:
            if tile_object.type == 'Player':
                self.player.position.x = tile_object.x
                self.player.position.y = tile_object.y
                self.player.hit_rect.x = tile_object.x
                self.player.hit_rect.y = tile_object.y
            if tile_object.type == 'Block':
                if tile_object.name == 'bounce':
                    direction = tile_object.Direction
                else:
                    direction = None
                sprites.Block(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height,
                              tile_object.name, direction)
            if tile_object.type == 'Interactable':
                if tile_object.name == 'button':
                    ability = tile_object.Ability
                else:
                    ability = None

                sprites.Interactable(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height,
                                     tile_object.name, self.button_down_img, self.button_up_img, ability)

        self.camera = tilemap.Camera(self.map.width, self.map.height)

    # Combine next_level and restart_level into one
    def next_level(self):
        self.interactables.empty()
        self.blocks.empty()
        self.bullets.empty()
        self.level_number += 1
        self.load_level(self.levels[self.level_number])

    def restart_level(self):
        self.interactables.empty()
        self.blocks.empty()
        self.bullets.empty()
        self.load_level(self.levels[self.level_number])

    def update(self):
        # stop using all_sprites eventually for more control over how everything updates
        self.all_sprites.update()
        self.player_sprites.update()
        self.interactables.update()
        self.camera.update(self.player)

    def events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    if self.playing:
                        self.playing = False
                    self.running = False

                if event.key == pygame.K_TAB:
                    self.show_debug()

            if event.type == pygame.JOYBUTTONDOWN:

                # this might need to be cleaned up a bit
                if event.button == settings.JOYBUTTONS['A']:
                    if self.joystick.get_axis(settings.JOYAXIS['LeftVertical']) > 0.85:
                        self.player.platform_drop()
                    elif self.player.wall_grabbing and self.player.check_airborne() and self.player.current_energy > 0:
                        self.player.wall_jump()
                    elif not self.player.check_airborne():
                        self.player.jump()
                    elif self.player.check_airborne() and self.player.can_double_jump and not self.player.double_jumping:
                        self.player.double_jump()

                if event.button == settings.JOYBUTTONS['B']:
                    if self.player.ranged_attacking is False:
                        self.player.ranged_attack()

                if event.button == settings.JOYBUTTONS['X']:
                    pass
                    # turned off melee attack until animation is better
                    #if self.player.sword_attacking is False:
                        #self.player.thrust_attack()

                if event.button == settings.JOYBUTTONS['Y']:
                    for object in self.interactables:
                        if object.name == 'exit' and self.player.rect.colliderect(object.rect):
                                self.next_level()
                        if object.name == 'button' and self.player.rect.colliderect(object.rect):
                            object.state = not object.state
                            if object.ability == 'Double Jump':
                                self.player.can_double_jump = True
                                self.draw_text('You Gained Double Jump!', 18, settings.WHITE, 150, 100, True)
                            if object.ability == 'Sprint':
                                self.player.can_sprint = True
                                self.draw_text('You Gained Sprint!', 18, settings.WHITE, 150, 150, True)

                if event.button == settings.JOYBUTTONS['LeftBumper']:
                    if self.player.can_teleport:
                        self.player.joystick_teleport('left')

                if event.button == settings.JOYBUTTONS['RightBumper']:
                    if self.player.can_teleport:
                        self.player.joystick_teleport('right')

            if event.type == pygame.JOYBUTTONUP:
                if event.button == settings.JOYBUTTONS['A']:
                    self.player.jump_cut()

    def draw(self):
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))

        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        for sprite in self.interactables:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        for sprite in self.player_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        self.draw_bar(5, 5, self.player.current_energy / self.player.max_energy)

        # everything you want to see when debugging / Toggle with TAB
        if self.debug:
            self.draw_debug()

        # display frame
        pygame.display.flip()

    def draw_bar(self, x, y, percentage):
        color = settings.BLUE
        if percentage < 0:
            percentage = 0
        BAR_LENGTH = 100
        BAR_HEIGHT = 10
        filled = percentage * BAR_LENGTH
        outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        filled_rect = pygame.Rect(x, y, filled, BAR_HEIGHT)
        pygame.draw.rect(self.screen, settings.BLACK, outline_rect)
        pygame.draw.rect(self.screen, color, filled_rect)
        pygame.draw.rect(self.screen, settings.WHITE, outline_rect, 2)

    def draw_text(self, text, size, color, x, y, centered):
        font = pygame.font.Font(settings.FONT, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.x = x
        text_rect.y = y
        if centered:
            text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    # this needs to be cleaned up
    # probably introduce a state machine soon
    def show_start_screen(self):
        waiting = True
        while waiting:
            self.clock.tick(settings.FPS)

            # Draw All Text To Screen
            self.draw_text(settings.TITLE, 60, settings.WHITE, settings.WIDTH / 2, settings.HEIGHT / 4, True)
            self.draw_text('Press a joystick button to play', 30, settings.WHITE, settings.WIDTH / 2,
                           settings.HEIGHT / 2, True)
            self.draw_text('Press the escape button to quit', 20, settings.WHITE, settings.WIDTH / 2,
                           settings.HEIGHT / 2 + 50, True)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.running = False

                if event.type == pygame.JOYBUTTONDOWN:
                    waiting = False

    def show_debug(self):
        self.debug = not self.debug

    def draw_debug(self):
        self.screen.blit(self.player.hit_image, self.camera.apply_rect(self.player.hit_rect))