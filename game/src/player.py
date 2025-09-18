import pygame as pg
from conf import tile_size

class Player(pg.sprite.Sprite):
    def __init__(self, x, y, controls):
        pg.sprite.Sprite.__init__(self)
        try:
            img = pg.image.load("assets/mine/player.png")
            self.image = pg.transform.scale(img, (tile_size, tile_size * 2))
        except:
            self.image = pg.Surface((tile_size, tile_size * 2))
            self.image.fill((0, 0, 255))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.controls = controls

    def update(self, world, enemy_group, oj_group):
        dX = 0
        dY = 0
        self.direction = 0
        
        key = pg.key.get_pressed()
        if key[self.controls['left']]:
            dX -= 5
            self.direction = -1
        if key[self.controls['right']]:
            dX += 5
            self.direction = 1
        if key[self.controls['up']] and not self.jumped:
            self.vel_y = -15
            self.jumped = True

        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dY += self.vel_y

        nX = self.rect.x + dX
        nY = self.rect.y + dY

        for tile in world.tile_list:
            if tile[1].colliderect(pg.Rect(nX, self.rect.y, self.width, self.height)):
                dX = 0
                nX = self.rect.x
            if tile[1].colliderect(pg.Rect(self.rect.x, nY, self.width, self.height)):
                if self.vel_y < 0:
                    dY = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:
                    dY = tile[1].top - self.rect.bottom
                    self.vel_y = 0
                    self.jumped = False

        self.rect.x += dX
        self.rect.y += dY
        return self.check_collisions(world, enemy_group, oj_group)

    def check_collisions(self, world, enemy_group, oj_group):
        if pg.sprite.spritecollide(self, enemy_group, False): return -1
        if pg.sprite.spritecollide(self, oj_group, False): return -1
        for tile in world.level_transition_tiles:
            if self.rect.colliderect(tile[1]): return 2
        return 0
