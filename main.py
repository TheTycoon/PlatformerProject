import pygame
from os import path

import settings
import player
import sprites
import tilemap

class Game:
    def __init__(self):
        # initialize game window, sound, etc
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

        # show title
        #pygame.display.set_caption(settings.TITLE)

        self.running = True
        self.load_data()

    def new(self):
        # start a new game
        self.all_sprites = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.abilities = pygame.sprite.Group()

        # Initialize Map Objects
        for tile_object in self.map.tmxdata.objects:
            if tile_object.type == 'Player':
                self.player = player.Player(self, tile_object.x, tile_object.y)
            if tile_object.type == 'Block':
                sprites.Block(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height, tile_object.name)
            if tile_object.type == 'AbilityBlock':
                sprites.AbilityBlock(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height, tile_object.name)

        self.camera = tilemap.Camera(self.map.width, self.map.height)

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

        # load Tiled map stuff
        self.map = tilemap.Map(path.join(self.map_folder, 'testmap.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

    def events(self):
        # Game Loop - Events
        for event in pygame.event.get():

            # quit event / close window
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            # Keyboard input events below
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.player.check_airborne():
                        self.player.jump()
                    if self.player.check_airborne() and self.player.can_double_jump and not self.player.double_jumping:
                        self.player.double_jump()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.player.jump_cut()

            # Joystick/controller events below
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == settings.JOYSTICK['A']:
                    if not self.player.check_airborne():
                        self.player.jump()
                    if self.player.check_airborne() and self.player.can_double_jump and not self.player.double_jumping:
                        self.player.double_jump()

            if event.type == pygame.JOYBUTTONUP:
                if event.button == settings.JOYSTICK['A']:
                    self.player.jump_cut()


    def draw(self):
        # show FPS
        pygame.display.set_caption("{:.2f}".format(self.clock.get_fps()))

        # DRAW STUFF
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.all_sprites:
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

game = Game()
while game.running:
    game.new()
    game.run()

pygame.quit()


