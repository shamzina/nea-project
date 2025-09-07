import pygame as pg
# from pygame.locals import *
# -^ only commented cause its not being used and nvim is crying about it #
# WARNING: /* making it clear now, #// means for school and
# WARNING: comment # means personal (delete personals) */

# // Initialize pygame lib
pg.init()

# // set the screen width and height
sc_width = 1280
sc_height = 720

# // create a blank window and give it a title
screen = pg.display.set_mode((sc_width, sc_height))
pg.display.set_caption("platformer")

# // load images
bg_img = pg.image.load("assets/mine/level1background.png")
bg_img = pg.transform.scale(bg_img, (1280, 720))


# --------------------------------------------------------------

tile_size = 40

# once ive finished player1 ill just copy it and make player 2 using wasd :) #


class Player1():
    def __init__(self, x, y):
        img = pg.image.load("assets/mine/player.png")
        self.image = pg.transform.scale(img, (40, 80))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False

    def update(self):
        # set change in Y and X
        dX = 0
        dY = 0
        # inputs
        key = pg.key.get_pressed()

        if key[pg.K_UP] and self.jumped == False:
            self.vel_y = -15
            self.jumped = True

        if key[pg.K_LEFT]:
            dX -= 5

        if key[pg.K_RIGHT]:
            dX += 5

        # add gravity

        self.vel_y += 1

        if self.vel_y > 8:
            self.vel_y = 8

        dY += self.vel_y

        # check for collisons

        for i in world.tile_list:
            # check x axis
            if i[1].colliderect(self.rect.x + dX, self.rect.y, self.width, self.height):
                dX = 0

            # check y axis
            if i[1].colliderect(self.rect.x, self.rect.y + dY, self.width, self.height):
                # check if under ground
                if self.vel_y < 0:
                    dY = i[1].bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y > 0:
                    dY = i[1].top - self.rect.bottom
                    self.vel_y = 0
                    self.jumped = False

        # update coordinates of player
        self.rect.x += dX
        self.rect.y += dY

        if self.rect.bottom > sc_height:
            self.rect.bottom = sc_height
            dY = 0

        # display player
        screen.blit(self.image, self.rect)
        pg.draw.rect(screen, (255, 255, 255), self.rect, 2)


class World():
    def __init__(self, data):
        self.tile_list = []

        tile_img = pg.image.load("assets/mine/level1tile.png")
        rCount = 0

        for i in data:
            cCount = 0
            for j in i:
                if j == 1:
                    img = pg.transform.scale(tile_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = cCount * tile_size
                    img_rect.y = rCount * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if j == 2:
                    enmy = Enemy(cCount * tile_size, rCount * tile_size)
                    enemy_group.add(enmy)

                cCount += 1
            rCount += 1

    def draw(self):
        for i in self.tile_list:
            screen.blit(i[0], i[1])
            pg.draw.rect(screen, (255, 255, 255), i[1], 2)


class Enemy(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)

        self.image = pg.image.load("assets/mine/enemy.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if self.move_counter > 50:
            self.move_direction *= -1
            self.move_counter *= -1




world_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]
# TODO: -^ PLEASE find a way to do this shit normally cause i might commit suicide #
# --------------------------------------------------------------

# clock so we can lock FPS to 60
clock = pg.time.Clock()

# // run the game loop

plr = Player1(100, sc_height - 130)
enemy_group = pg.sprite.Group()
world = World(world_data)

run = True
while run:
    # fps check
    print(f"FPS: {int(clock.get_fps())}")
    # display images
    screen.blit(bg_img, (0, 0))
    world.draw()

    enemy_group.update()
    enemy_group.draw(screen)
    plr.update()

    print(world.tile_list)

    # // event loop
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            run = False

    pg.display.update()

    clock.tick(60)

pg.quit()
