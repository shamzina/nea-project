#ifndef GAME_H
#define GAME_H

#include <SDL3/SDL.h>
#include <stdio.h>
#include "player.h"
#include "level.h"
#include "collision.h"
#include "tether.h"

#define TARGET_FPS 60
#define FRAME_TIME_MS (1000.0f / TARGET_FPS)

// Game states
typedef enum {
    STATE_MENU,
    STATE_PLAYING,
    STATE_PAUSED,
    STATE_GAME_OVER,
    STATE_VICTORY,
    STATE_QUIT
} GameStateType;

// Button structure
typedef struct {
    SDL_FRect rect;
    char text[50];
    int is_hovered;
    int is_clicked;
    SDL_Color normal_color;
    SDL_Color hover_color;
} Button;

// Main game structure
typedef struct {
    SDL_Window* window;
    SDL_Renderer* renderer;

    GameStateType current_state;
    bool run;
    float dtime;
    Uint64 lftime;
    Uint64 perf_freq;

    Player player1;
    Player player2;
    Level current_level;
    Tether tether;

    Button menu_buttons[2];

    int current_level_index;
    float game_time;
    int attempts;
} Game;

// Core functions
int game_init(Game* game);
void game_run(Game* game);
void game_cleanup(Game* game);

#endif // GAME_H
