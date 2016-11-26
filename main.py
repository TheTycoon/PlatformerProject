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
        #pygame.mixer.init()
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.clock = pygame.time.Clock()

        # show title
        #pygame.display.set_caption(settings.TITLE)

        self.running = True
        self.load_data()

    def new(self):
        # start a new game
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()

        # Initialize Map Objects
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'Player':
                self.player = player.Player(self, tile_object.x, tile_object.y)
            if tile_object.name == 'Wall':
                sprites.Wall(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)

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

        # load Tiled map stuff
        self.map = tilemap.Map(path.join(self.map_folder, 'map1.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()

    def events(self):
        # Game Loop - Events
        for event in pygame.event.get():

            # quit event / close window
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.player.jump_cut()
                if not self.player.jumping and (event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT):
                    self.player.velocity.y = 0

    def draw(self):
        # show FPS
        pygame.display.set_caption("{:.2f}".format(self.clock.get_fps()))

        # DRAW STUFF
        self.screen.blit(self.map_img, self.map_rect)
        self.all_sprites.draw(self.screen)

        # display frame
        pygame.display.flip()

game = Game()
while game.running:
    game.new()
    game.run()

pygame.quit()


