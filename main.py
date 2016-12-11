import pygame
from os import path

import settings
import player
import sprites
import tilemap

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.clock = pygame.time.Clock()

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
        self.blocks = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.interactables = pygame.sprite.Group()
        self.abilities = pygame.sprite.Group()

        self.levels = ['testmap.tmx', 'level1.tmx', 'level2.tmx', 'level3.tmx', 'level4.tmx', 'level5.tmx',
                       'level6.tmx']
        self.player = player.Player(self, 0, 0,)

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

        self.powerup_img = pygame.image.load(path.join(self.img_folder, 'metal_ball.png')).convert_alpha()



    def load_level(self, mapname):
        self.map = tilemap.Map(path.join(self.map_folder, mapname))    #testmap.tmx is current testing ground
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.initialize_level()

    def initialize_level(self):
        for tile_object in self.map.tmxdata.objects:
            if tile_object.type == 'Player':
                self.player.position.x = tile_object.x
                self.player.position.y = tile_object.y
                self.player.rect.x = tile_object.x
                self.player.rect.y = tile_object.y
            if tile_object.type == 'Block':
                if tile_object.name == 'bounce':
                    direction = tile_object.Direction
                else:
                    direction = None
                sprites.Block(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height, tile_object.name, direction)
            if tile_object.type == 'Interactable':
                sprites.Interactable(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height, tile_object.name)
            if tile_object.type == 'Ability':
                sprites.Ability(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height, tile_object.name)
        self.camera = tilemap.Camera(self.map.width, self.map.height)

    def next_level(self):
        self.interactables.empty()
        self.blocks.empty()
        self.level_number += 1
        self.load_level(self.levels[self.level_number])

    def restart_level(self):
        self.interactables.empty()
        self.blocks.empty()
        self.load_level(self.levels[self.level_number])

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

        print(self.player.velocity)


    def events(self):
        # Game Loop - Events
        for event in pygame.event.get():

            # quit event / close window
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            if event.type == pygame.JOYBUTTONDOWN:

                if event.button == settings.JOYBUTTONS['A']:
                    if self.joystick.get_axis(settings.JOYAXIS['LeftVertical']) > 0.85:
                        self.player.platform_drop()
                    elif not self.player.check_airborne():
                        self.player.jump()
                    elif self.player.check_airborne() and self.player.can_double_jump and not self.player.double_jumping:
                        self.player.double_jump()

                if event.button == settings.JOYBUTTONS['Y']:
                    for object in self.interactables:
                        if object.name == 'exit':
                            if self.player.rect.colliderect(object.rect):
                                self.next_level()

                if event.button == settings.JOYBUTTONS['LeftBumper']:
                    self.player.joystick_air_dash('left')

                if event.button == settings.JOYBUTTONS['RightBumper']:
                    self.player.joystick_air_dash('right')


            if event.type == pygame.JOYBUTTONUP:
                if event.button == settings.JOYBUTTONS['A']:
                    self.player.jump_cut()





            # # Keyboard input events below || NOT CURRENTLY SUPPORTING KEYBOARD
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE:
            #         if not self.player.check_airborne():
            #             self.player.jump()
            #         if self.player.check_airborne() and self.player.can_double_jump and not self.player.double_jumping:
            #             self.player.double_jump()
            # if event.type == pygame.KEYUP:
            #     if event.key == pygame.K_SPACE:
            #         self.player.jump_cut()

            # Joystick/controller events below


    def draw(self):
        # show FPS
        pygame.display.set_caption("{:.2f}".format(self.clock.get_fps()))

        # DRAW STUFF
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        for sprite in self.abilities:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        self.draw_bar(5, 5, self.player.current_energy / self.player.max_energy)

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

    def show_start_screen(self):
        waiting = True
        while waiting:
            self.clock.tick(settings.FPS)

            # Draw All Text To Screen
            self.draw_text(settings.TITLE, 60, settings.WHITE, settings.WIDTH / 2, settings.HEIGHT / 4, True)
            self.draw_text('Press a joystick button to play', 30, settings.WHITE, settings.WIDTH / 2, settings.HEIGHT / 2, True)
            self.draw_text('Press the escape button to quit', 20, settings.WHITE, settings.WIDTH / 2, settings.HEIGHT / 2 + 50, True)
            pygame.display.flip()

            for event in pygame.event.get():
                # Quit if player exits game
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.running = False

                if event.type == pygame.JOYBUTTONDOWN:
                    waiting = False


game = Game()
game.new()
game.show_start_screen()

while game.running:
    game.run()

pygame.quit()


