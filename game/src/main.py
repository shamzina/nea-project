import pygame as pg
from conf import *
from player import Player
from world import World

# Initialize pygame
pg.init()

# Create window and rendering surface
screen = pg.display.set_mode((window_width, window_height))
pg.display.set_caption("Platformer")
render_surface = pg.Surface((render_width, render_height))

# Define font
font = pg.font.SysFont('Bauhaus 93', 50)

# Load images for UI
try:
    bg_img = pg.image.load("assets/mine/level1background.png")
    bg_img = pg.transform.scale(bg_img, (render_width, render_height))
except:
    bg_img = pg.Surface((render_width, render_height)); bg_img.fill((50, 50, 100))
try:
    menu_bg_img = pg.image.load("assets/mine/level1background.png")
    menu_bg_img = pg.transform.scale(menu_bg_img, (render_width, render_height))
except:
    menu_bg_img = pg.Surface((render_width, render_height)); menu_bg_img.fill((100, 50, 50))
try:
    res_img = pg.image.load("assets/mine/restart_btn.png")
    res_img = pg.transform.scale(res_img, (100, 50))
except:
    res_img = pg.Surface((100, 50)); res_img.fill((200, 0, 0))
try:
    start_img = pg.image.load("assets/mine/start_btn.png")
    start_img = pg.transform.scale(start_img, (100, 50))
except:
    start_img = pg.Surface((100, 50)); start_img.fill((0, 200, 0))
try:
    exit_img = pg.image.load("assets/mine/exit_btm.png")
    exit_img = pg.transform.scale(exit_img, (100, 50))
except:
    exit_img = pg.Surface((100, 50)); exit_img.fill((0, 0, 200))

# --- Helper Classes & Functions ---
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
        self.rect = self.image.get_rect(topleft=(x,y))
        self.clicked = False

    def draw(self, surface):
        action = False
        mouse_pos = pg.mouse.get_pos()
        scaled_mouse_pos = (mouse_pos[0] * render_width / window_width, mouse_pos[1] * render_height / window_height)
        if self.rect.collidepoint(scaled_mouse_pos):
            if pg.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True; action = True
        if not pg.mouse.get_pressed()[0]: self.clicked = False
        surface.blit(self.image, self.rect)
        return action

# --- Game State Variables ---
level = 0
game_over = 0
paused = False
world = None
clock = pg.time.Clock()

# --- Sprite Groups ---
player_group = pg.sprite.Group()
enemy_group = pg.sprite.Group()
oj_group = pg.sprite.Group()

# --- UI Buttons ---
start_button = Button(render_width//2 - 50, render_height//2, start_img)
exit_button = Button(render_width//2 - 50, render_height//2 - 50, exit_img)
res_button = Button(render_width//2 - 50, render_height//2 + 100, res_img)

def load_level(level_num):
    global world, game_over
    player_group.empty()
    enemy_group.empty()
    oj_group.empty()
    
    try:
        level_path = f"levels/level_{level_num}.txt"
        with open(level_path, 'r') as f: data = [list(map(int, line.strip().split())) for line in f]
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading level {level_num}: {e}"); return False
    
    # Create world, passing sprite groups to populate them
    world = World(data, enemy_group, oj_group)
    
    # Create players
    player1_controls = {'up': pg.K_UP, 'left': pg.K_LEFT, 'right': pg.K_RIGHT}
    player2_controls = {'up': pg.K_w, 'left': pg.K_a, 'right': pg.K_d}
    player_group.add(Player(100, render_height - 130, player1_controls))
    player_group.add(Player(150, render_height - 130, player2_controls))
    
    game_over = 0
    print(f"Loaded level {level_num}")
    return True

# --- Main Game Loop ---
run = True
while run:
    clock.tick(30)
    
    if level == 0: # Main Menu
        render_surface.blit(menu_bg_img, (0, 0))
        if start_button.draw(render_surface):
            if load_level(1): level = 1 
        if exit_button.draw(render_surface):
            exit()
    else: # In-game
        render_surface.blit(bg_img, (0, 0))
        if world: world.draw(render_surface)

        if game_over == 0:
            if not paused:
                enemy_group.update()
                for player in player_group:
                    result = player.update(world, enemy_group, oj_group)
                    if result == -1: game_over = -1; break
                    elif result == 2:
                        next_level_num = level + 1
                        if next_level_num > max_levels:
                            print("You've completed all levels!"); level = 0
                        elif load_level(next_level_num): level = next_level_num
                        else: level = 0
                        break
        
        player_group.draw(render_surface)
        enemy_group.draw(render_surface)
        oj_group.draw(render_surface)

        if game_over == -1 and res_button.draw(render_surface):
            load_level(level)
        
        if paused: draw_text('PAUSED', font, white, render_width // 2 - 80, render_height // 2)

    # Scale render surface to window and update display
    scaled_surface = pg.transform.scale(render_surface, (window_width, window_height))
    screen.blit(scaled_surface, (0, 0))
    pg.display.update()

    # Event Handler
    for ev in pg.event.get():
        if ev.type == pg.QUIT: run = False
        elif ev.type == pg.KEYDOWN:
            if ev.key == pg.K_SPACE: paused = not paused
            if ev.key == pg.K_0: level = 0

pg.quit()
