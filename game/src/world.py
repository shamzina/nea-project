import pygame as pg
from conf import tile_size
from enemies import Enemy, OJ # Import entity classes

class World():
    def __init__(self, data, enemy_group, oj_group):
        self.tile_list = []
        self.level_transition_tiles = []
        
        try:
            tile_img = pg.image.load("assets/mine/level1tile.png")
            tile_img = pg.transform.scale(tile_img, (tile_size, tile_size))
        except:
            tile_img = pg.Surface((tile_size, tile_size))
            tile_img.fill((100, 100, 100))
            
        try:
            self.transition_tile_img = pg.image.load("assets/mine/levelstile.png")
            self.transition_tile_img = pg.transform.scale(self.transition_tile_img, (tile_size, tile_size))
            color_image = pg.Surface(self.transition_tile_img.get_size()).convert_alpha()
            color_image.fill((0, 255, 0, 128))
            self.transition_tile_img.blit(color_image, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        except:
            self.transition_tile_img = pg.Surface((tile_size, tile_size))
            self.transition_tile_img.fill((0, 255, 0))

        for r_idx, row in enumerate(data):
            for c_idx, tile_val in enumerate(row):
                if tile_val == 1:
                    img_rect = tile_img.get_rect(topleft=(c_idx * tile_size, r_idx * tile_size))
                    self.tile_list.append((tile_img, img_rect))
                elif tile_val == 2:
                    enemy_group.add(Enemy(c_idx * tile_size, r_idx * tile_size))
                elif tile_val == 3:
                    oj_group.add(OJ(c_idx * tile_size, r_idx * tile_size))
                elif tile_val == 9:
                    img_rect = self.transition_tile_img.get_rect(topleft=(c_idx * tile_size, r_idx * tile_size))
                    self.level_transition_tiles.append((self.transition_tile_img, img_rect))

    def draw(self, surface):
        for tile in self.tile_list:
            surface.blit(tile[0], tile[1])
        for tile in self.level_transition_tiles:
            surface.blit(tile[0], tile[1])
