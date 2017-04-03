#clonedjump - Platformer made in pygame for educational purposes


import pygame as pg
import random
from settings import *
from sprites import *
from os import path

class Game:
    def __init__(self):
        #initialize game window, etc
        pg.mixer.pre_init(44100, -16, 2, 2048)
        pg.mixer.init()
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()
        
    def load_data(self):
        # load high score
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, "img")
        with open(path.join(self.dir, HS_FILE), "r") as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        # load spritesheet image
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        
        # load sound
        self.snd_dir = path.join(self.dir, "snd")
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, "sfx_movement_jump1.wav"))
        
    def new(self):
        #start a new game and add all sprites to a group
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        for plat in PLATFORM_LIST:
            p = Platform(self, *plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
        pg.mixer.music.load(path.join(self.snd_dir, "Happy_Tune.ogg"))
        self.run()

    def run(self):
        #Game Loop
        pg.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)

    def update(self):
        #game loop update
        self.all_sprites.update()
        #check if player hits a platform - only if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.y < lowest.rect.centery:
                    self.player.pos.y = lowest.rect.top
                    self.player.vel.y = 0
                    self.player.jumping = False

        #if player reaches top 1/4 of screen
        if self.player.rect.top <= HEIGHT / 4:
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y),2 )
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10
                    
        # Die
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

        #spawn new platforms to keep average number with randomized size and placement
        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            p = Platform(self, random.randrange(0, WIDTH - width),
                    random.randrange(-75, 30))
            self.platforms.add(p)
            self.all_sprites.add(p)

    def events(self):
        #game loop events
        for event in pg.event.get():
            #check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()

    def draw(self):
        #game loop draw
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        #After drawing everything, flip display
        pg.display.flip()

    def show_start_screen(self):
        #splash screen
        pg.mixer.music.load(path.join(self.snd_dir, "Yippee.ogg"))
        pg.mixer.music.play(loops=-1)
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Arrows to move, Space to jump", 22, BLACK, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press any key to start", 20, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def show_go_screen(self):
        #game over screen
        if not self.running:
            return
        pg.mixer.music.load(path.join(self.snd_dir, "Yippee.ogg"))
        pg.mixer.music.play(loops=-1)
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score: " + str(self.score), 22, BLACK, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press any key to play again", 20, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("New Highscore!", 22, BLACK, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), "w") as f:
                f.write(str(self.score))
        else:
            self.draw_text("High Score: " + str(self.highscore), 22, BLACK, WIDTH / 2, HEIGHT / 2 + 40)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)
        
    def wait_for_key(self):
        # waiting for keypress between splash/game over and the game
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False
        
    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color) # True for anti-aliasing
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
