import pygame as pg

# Initialize pygame lib
pg.init()

# Set the rendering resolution
render_width = 800
render_height = 450

# Set the window size
window_width = 1280
window_height = 720

# Global level variable (0 = main menu, 1 = level 1, 2 = level 2, etc.)
level = 0
game_over = 0

# Create a blank window and give it a title
screen = pg.display.set_mode((window_width, window_height))
pg.display.set_caption("platformer")

# Create a surface for rendering at the lower resolution
render_surface = pg.Surface((render_width, render_height))

# Load images (using placeholder colors for missing images)
try:
    bg_img = pg.image.load("assets/mine/level1background.png")
    bg_img = pg.transform.scale(bg_img, (render_width, render_height))
except:
    bg_img = pg.Surface((render_width, render_height))
    bg_img.fill((50, 50, 100))  # Blue background if image not found

try:
    menu_bg_img = pg.image.load("assets/mine/level1background.png")
    menu_bg_img = pg.transform.scale(menu_bg_img, (render_width, render_height))
except:
    menu_bg_img = pg.Surface((render_width, render_height))
    menu_bg_img.fill((100, 50, 50))  # Red background if image not found

try:
    res_img = pg.image.load("assets/mine/restart_btn.png")
    res_img = pg.transform.scale(res_img, (100, 50))
except:
    res_img = pg.Surface((100, 50))
    res_img.fill((200, 0, 0))  # Red button if image not found

try:
    start_img = pg.image.load("assets/mine/restart_btn.png")
    start_img = pg.transform.scale(start_img, (100, 50))
except:
    start_img = pg.Surface((100, 50))
    start_img.fill((0, 200, 0))  # Green button if image not found

# Using 20px tile size for optimal performance at 30FPS
tile_size = 20

# Calculate the grid size based on tile size
grid_width = render_width // tile_size
grid_height = render_height // tile_size


class Button():
    def __init__(self, x, y, image, scale=1.0):
        self.image = image
        if scale != 1.0:
            width = int(self.image.get_width() * scale)
            height = int(self.image.get_height() * scale)
            self.image = pg.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        # Get mouse position relative to render surface
        mouse_pos = pg.mouse.get_pos()
        # Scale mouse position to render surface coordinates
        scaled_mouse_x = mouse_pos[0] * render_width / window_width
        scaled_mouse_y = mouse_pos[1] * render_height / window_height
        scaled_mouse_pos = (scaled_mouse_x, scaled_mouse_y)

        if self.rect.collidepoint(scaled_mouse_pos):
            if pg.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                action = True

        if not pg.mouse.get_pressed()[0]:
            self.clicked = False

        render_surface.blit(self.image, self.rect)
        return action


class Player1():
    def __init__(self, x, y):
        try:
            img = pg.image.load("assets/mine/player.png")
            self.image = pg.transform.scale(img, (tile_size, tile_size * 2))
        except:
            self.image = pg.Surface((tile_size, tile_size * 2))
            self.image.fill((0, 0, 255))  # Blue player if image not found

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0

    def update(self):
        # set change in Y and X
        dX = 0
        dY = 0

        # reset movement direction
        self.direction = 0

        # get keypresses
        key = pg.key.get_pressed()
        if key[pg.K_LEFT]:
            dX -= 5
            self.direction = -1
        if key[pg.K_RIGHT]:
            dX += 5
            self.direction = 1
        if key[pg.K_UP] and not self.jumped:
            self.vel_y = -15
            self.jumped = True

        # add gravity
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dY += self.vel_y

        # Pre-calculate potential new position
        new_x = self.rect.x + dX
        new_y = self.rect.y + dY

        # check for collisions - only check nearby tiles for performance
        start_x = max(0, (new_x // tile_size) - 1)
        end_x = min(grid_width, (new_x + self.width) // tile_size + 2)
        start_y = max(0, (new_y // tile_size) - 1)
        end_y = min(grid_height, (new_y + self.height) // tile_size + 2)

        # Check collisions only with nearby tiles
        for tile in world.tile_list:
            tile_rect = tile[1]
            # Skip tiles that are too far away
            if (tile_rect.x < (start_x * tile_size) or tile_rect.x > (end_x * tile_size) or
                tile_rect.y < (start_y * tile_size) or tile_rect.y > (end_y * tile_size)):
                continue

            # check for collision in x direction
            if tile_rect.colliderect(pg.Rect(new_x, self.rect.y, self.width, self.height)):
                dX = 0
                new_x = self.rect.x

            # check for collision in y direction
            if tile_rect.colliderect(pg.Rect(self.rect.x, new_y, self.width, self.height)):
                # check if below the ground (jumping)
                if self.vel_y < 0:
                    dY = tile_rect.bottom - self.rect.top
                    self.vel_y = 0
                # check if above the ground (falling)
                elif self.vel_y >= 0:
                    dY = tile_rect.top - self.rect.bottom
                    self.vel_y = 0
                    self.jumped = False

        # update player coordinates
        self.rect.x += dX
        self.rect.y += dY

        # draw player onto render surface
        render_surface.blit(self.image, self.rect)

        return self.check_collisions()

    def check_collisions(self):
        # enemy collide?
        if pg.sprite.spritecollide(self, enemy_group, False):
            return -1

        if pg.sprite.spritecollide(self, oj_group, False):
            return -1

        # Check for level transition tile (9)
        for tile in world.level_transition_tiles:
            if self.rect.colliderect(tile[1]):
                return 2  # Signal to go to next level

        return 0


class World():
    def __init__(self, data):
        self.tile_list = []
        self.level_transition_tiles = []  # List to store level transition tiles

        try:
            tile_img = pg.image.load("assets/mine/level1tile.png")
            tile_img = pg.transform.scale(tile_img, (tile_size, tile_size))
        except:
            tile_img = pg.Surface((tile_size, tile_size))
            tile_img.fill((100, 100, 100))  # Gray tiles if image not found

        # Create a special tile for level transitions (tile 9)
        try:
            self.transition_tile_img = pg.image.load("assets/mine/levelstile.png")
            self.transition_tile_img = pg.transform.scale(self.transition_tile_img, (tile_size, tile_size))
            # Make it a different color to distinguish it
            color_image = pg.Surface(self.transition_tile_img.get_size()).convert_alpha()
            color_image.fill((0, 255, 0, 128))  # Green with transparency
            self.transition_tile_img.blit(color_image, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        except:
            self.transition_tile_img = pg.Surface((tile_size, tile_size))
            self.transition_tile_img.fill((0, 255, 0))  # Green transition tile if image not found

        rCount = 0

        for i in data:
            cCount = 0
            for j in i:
                if j == 1:
                    img = tile_img
                    img_rect = img.get_rect()
                    img_rect.x = cCount * tile_size
                    img_rect.y = rCount * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if j == 2:
                    enmy = Enemy(cCount * tile_size, rCount * tile_size)
                    enemy_group.add(enmy)
                if j == 3:
                    oj = OJ(cCount * tile_size, rCount * tile_size)
                    oj_group.add(oj)
                if j == 9:  # Level transition tile
                    img = self.transition_tile_img
                    img_rect = img.get_rect()
                    img_rect.x = cCount * tile_size
                    img_rect.y = rCount * tile_size
                    tile = (img, img_rect)
                    self.level_transition_tiles.append(tile)

                cCount += 1
            rCount += 1

    def draw(self):
        for i in self.tile_list:
            render_surface.blit(i[0], i[1])
        # Draw level transition tiles
        for i in self.level_transition_tiles:
            render_surface.blit(i[0], i[1])


class Enemy(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)

        try:
            self.image = pg.image.load("assets/mine/enemy.png")
            self.image = pg.transform.scale(self.image, (tile_size, tile_size))
        except:
            self.image = pg.Surface((tile_size, tile_size))
            self.image.fill((255, 0, 0))  # Red enemy if image not found

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
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
            self.image.fill((255, 165, 0))  # Orange juice if image not found

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Level data definitions
# Level 1
world_data_1 = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Level 2 (example)
world_data_2 = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Level 3 (example)
world_data_3 = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Dictionary to map level numbers to world data
level_data = {
    1: world_data_1,
    2: world_data_2,
    3: world_data_3
    # Add more levels as needed: 4: world_data_4, etc.
}

# clock so we can lock FPS to 30
clock = pg.time.Clock()

# Initialize game objects
plr = None
enemy_group = pg.sprite.Group()
oj_group = pg.sprite.Group()
world = None

# Create buttons
start_button = Button(render_width//2 - 50, render_height//2, start_img)
res_button = Button(render_width//2 - 50, render_height//2 + 100, res_img)

# Function to reset/load a level
def load_level(level_num):
    global plr, enemy_group, oj_group, world, game_over
    if level_num in level_data:
        enemy_group.empty()
        oj_group.empty()
        world = World(level_data[level_num])
        plr = Player1(100, render_height - 130)
        game_over = 0
        print(f"Loaded level {level_num}")
    else:
        print(f"Level {level_num} not found!")

# Main game loop
run = True
while run:
    # Limit FPS to 30
    clock.tick(30)

    # Clear the render surface
    if level == 0:  # Main menu
        render_surface.blit(menu_bg_img, (0, 0))
        if start_button.draw():
            level = 1
            load_level(level)
    else:  # Game level
        render_surface.blit(bg_img, (0, 0))
        world.draw()

        if game_over == 0:
            # Update game objects
            enemy_group.update()
            result = plr.update()

            if result == -1:  # Player died
                game_over = -1
            elif result == 2:  # Player reached level transition tile
                level += 1
                if level in level_data:
                    load_level(level)
                else:
                    print("You've completed all levels!")
                    level = 0  # Return to main menu after completing all levels

        # Draw game objects
        enemy_group.draw(render_surface)
        oj_group.draw(render_surface)

        # Handle game over state
        if game_over == -1:
            if res_button.draw():
                # Reset the current level
                load_level(level)

    # Scale the render surface to the window size and display it
    scaled_surface = pg.transform.scale(render_surface, (window_width, window_height))
    screen.blit(scaled_surface, (0, 0))

    # Event handling
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            run = False
        # Add keyboard controls to switch levels for testing
        elif ev.type == pg.KEYDOWN:
            if ev.key == pg.K_0:  # Press 0 to go to main menu
                level = 0
            elif ev.key == pg.K_1:  # Press 1 to go to level 1
                level = 1
                load_level(level)
            elif ev.key == pg.K_2:  # Press 2 to go to level 2
                level = 2
                load_level(level)
            elif ev.key == pg.K_3:  # Press 3 to go to level 3
                level = 3
                load_level(level)

    pg.display.update()

pg.quit()
