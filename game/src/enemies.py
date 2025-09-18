import pygame as pg
from conf import tile_size

class Enemy(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        try:
            self.image = pg.image.load("assets/mine/enemy.png")
            self.image = pg.transform.scale(self.image, (tile_size, tile_size))
        except:
            self.image = pg.Surface((tile_size, tile_size))
            self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

class OJ(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        try:
            self.image = pg.image.load("assets/mine/orangejuice.png")
            self.image = pg.transform.scale(self.image, (tile_size, tile_size))
        except:
            self.image = pg.Surface((tile_size, tile_size))
            self.image.fill((255, 165, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
