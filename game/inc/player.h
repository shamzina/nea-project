#ifndef PLAYER_H
#define PLAYER_H

#include <SDL3/SDL.h>
#include <stdbool.h>
#include "level.h"
typedef struct {
    float x, y;           // Position
    float vx, vy;         // Velocity
    float w, h;           // Collision boundaries
    bool isgrounded;
    bool isjumping; 
    SDL_Color color; 
    const bool* keys;     // Keyboard state ref (bool* not uint8*)
    SDL_Keycode lkey, rkey, jkey; 
} Player;

void initPlayer(Player* p, float startx, float starty, 
                SDL_Keycode l, SDL_Keycode r, SDL_Keycode j, 
                SDL_Color c);
void player_upd(Player* p, float dtime, Level* level);
void plrRender(Player* p, SDL_Renderer* renderer);

#endif // PLAYER_H
