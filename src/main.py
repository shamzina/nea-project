import pygame as pg

# Initialize pygame lib
pg.init()

# Set the rendering resolution
render_width = 800
render_height = 450

# Set the window size
window_width = 1280
window_height = 720

# Global game state variables
level = 0  # 0 = main menu, 1 = level 1, etc.
game_over = 0
max_levels = 3 # The total number of level files you have
paused = False

# Create a blank window and give it a title
screen = pg.display.set_mode((window_width, window_height))
pg.display.set_caption("platformer")

# Create a surface for rendering at the lower resolution
render_surface = pg.Surface((render_width, render_height))

# Define font for text
font = pg.font.SysFont('Bauhaus 93', 50)
white = (255, 255, 255)

# Load images
try:
    bg_img = pg.image.load("assets/mine/level1background.png")
    bg_img = pg.transform.scale(bg_img, (render_width, render_height))
except:
    bg_img = pg.Surface((render_width, render_height))
    bg_img.fill((50, 50, 100))

try:
    menu_bg_img = pg.image.load("assets/mine/level1background.png")
    menu_bg_img = pg.transform.scale(menu_bg_img, (render_width, render_height))
except:
    menu_bg_img = pg.Surface((render_width, render_height))
    menu_bg_img.fill((100, 50, 50))

try:
    res_img = pg.image.load("assets/mine/restart_btn.png")
    res_img = pg.transform.scale(res_img, (100, 50))
except:
    res_img = pg.Surface((100, 50))
    res_img.fill((200, 0, 0))

try:
    start_img = pg.image.load("assets/mine/start_btn.png")
    start_img = pg.transform.scale(start_img, (100, 50))
except:
    start_img = pg.Surface((100, 50))
    start_img.fill((0, 200, 0))

# Game variables
tile_size = 20

# Function to draw text on the screen
def draw_text(text, text_font, text_col, x, y):
    img = text_font.render(text, True, text_col)
    render_surface.blit(img, (x, y))

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
        mouse_pos = pg.mouse.get_pos()
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

    def update(self, world):
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

        new_x = self.rect.x + dX
        new_y = self.rect.y + dY

        for tile in world.tile_list:
            if tile[1].colliderect(pg.Rect(new_x, self.rect.y, self.width, self.height)):
                dX = 0
                new_x = self.rect.x
            if tile[1].colliderect(pg.Rect(self.rect.x, new_y, self.width, self.height)):
                if self.vel_y < 0:
                    dY = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:
                    dY = tile[1].top - self.rect.bottom
                    self.vel_y = 0
                    self.jumped = False

        self.rect.x += dX
        self.rect.y += dY
        return self.check_collisions(world)

    def check_collisions(self, world):
        if pg.sprite.spritecollide(self, enemy_group, False): return -1
        if pg.sprite.spritecollide(self, oj_group, False): return -1
        for tile in world.level_transition_tiles:
            if self.rect.colliderect(tile[1]): return 2
        return 0

class World():
    def __init__(self, data):
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

    def draw(self):
        for tile in self.tile_list: render_surface.blit(tile[0], tile[1])
        for tile in self.level_transition_tiles: render_surface.blit(tile[0], tile[1])

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

clock = pg.time.Clock()
player_group = pg.sprite.Group()
enemy_group = pg.sprite.Group()
oj_group = pg.sprite.Group()
world = None
start_button = Button(render_width//2 - 50, render_height//2, start_img)
res_button = Button(render_width//2 - 50, render_height//2 + 100, res_img)

def load_level(level_num):
    global world, game_over
    player_group.empty()
    enemy_group.empty()
    oj_group.empty()
    try:
        level_path = f"assets/levels/level_{level_num}.txt"
        with open(level_path, 'r') as f:
            data = [list(map(int, line.strip().split())) for line in f]
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading level {level_num}: {e}")
        return False
    
    world = World(data)
    player1_controls = {'up': pg.K_UP, 'left': pg.K_LEFT, 'right': pg.K_RIGHT}
    player2_controls = {'up': pg.K_w, 'left': pg.K_a, 'right': pg.K_d}
    player_group.add(Player(100, render_height - 130, player1_controls))
    player_group.add(Player(150, render_height - 130, player2_controls))
    game_over = 0
    print(f"Loaded level {level_num}")
    return True

run = True
while run:
    clock.tick(30)
    if level == 0:
        render_surface.blit(menu_bg_img, (0, 0))
        # **FIXED LOGIC**: Only set level to 1 if loading is successful
        if start_button.draw():
            if load_level(1):
                level = 1
    else:
        render_surface.blit(bg_img, (0, 0))
        
        # This check prevents the crash if world is None
        if world:
            world.draw()

        if game_over == 0:
            if not paused:
                enemy_group.update()
                for player in player_group:
                    result = player.update(world)
                    if result == -1:
                        game_over = -1
                        break
                    elif result == 2:
                        next_level_num = level + 1
                        if next_level_num > max_levels:
                            print("You've completed all levels!")
                            level = 0
                        else:
                            # **FIXED LOGIC**: Check if next level loaded, otherwise return to menu
                            if load_level(next_level_num):
                                level = next_level_num
                            else:
                                level = 0
                        break
        
        player_group.draw(render_surface)
        enemy_group.draw(render_surface)
        oj_group.draw(render_surface)

        if game_over == -1 and res_button.draw():
            load_level(level)
        
        if paused:
            draw_text('PAUSED', font, white, render_width // 2 - 80, render_height // 2)

    scaled_surface = pg.transform.scale(render_surface, (window_width, window_height))
    screen.blit(scaled_surface, (0, 0))

    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            run = False
        elif ev.type == pg.KEYDOWN:
            if ev.key == pg.K_SPACE:
                paused = not paused
            if ev.key == pg.K_0:
                level = 0

    pg.display.update()

pg.quit()
