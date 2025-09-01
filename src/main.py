import pygame as pg
# from pygame.locals import *
# -^ only commented cause its not being used and nvim is crying about it #
# /* making it clear now, #// means for school and
# comment # means personal (delete personals) */

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
border_img = pg.image.load("assets/mine/level1border.png")
border_img = pg.transform.scale(border_img, (1280, 720))  # // fix img size
plr1_img = pg.image.load("assets/mine/player.png")
box1_img = pg.image.load("assets/mine/level1movableBox.png")
box1_img = pg.transform.scale(box1_img, ((5*40), (3*40)))
# the reason alot of scales are being * by 40 is
# that i made the levels in 32x18 but the window is 1280x720
# so the scale factor is 40 from 32x18 to 1280x720

# --------------------------------------------------------------

# // run the game loop

run = True
while run:
    # display images
    screen.blit(bg_img, (0, 0))
    screen.blit(border_img, (0, 0))

    # render one player (for now) since im still learning pygame
    screen.blit(plr1_img, ((1*40), (15*40)))

    # render the boxes i want the players to move
    screen.blit(box1_img, ((0), (0)))

    # // event loop
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            run = False

    pg.display.update()

pg.quit()
