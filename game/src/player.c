#include "player.h"
#include <stdio.h>
#include "collision.h"

#define GRAVITY 1000.0f
#define MOVE_SPEED 350.0f
#define JUMP_FORCE 500.0f

void initPlayer(Player* p, float startx, float starty, 
                SDL_Keycode left, SDL_Keycode right, SDL_Keycode jump, 
                SDL_Color color) {
    p->x = startx;
    p->y = starty;
    p->vx = 0;
    p->vy = 0;
    p->w = 32;
    p->h = 48;
    p->isgrounded = false;
    p->isjumping = false;
    p->color = color;
    p->lkey = left;
    p->rkey = right;
    p->jkey = jump;
    p->keys = SDL_GetKeyboardState(NULL);  
}

static void plrInput(Player* p) {
    // Horizontal movement
    p->vx = 0;
    
    SDL_Scancode left_scancode = SDL_GetScancodeFromKey(p->lkey, SDL_KMOD_NONE);
    SDL_Scancode right_scancode = SDL_GetScancodeFromKey(p->rkey, SDL_KMOD_NONE);
    SDL_Scancode jump_scancode = SDL_GetScancodeFromKey(p->jkey, SDL_KMOD_NONE);
    
    if (left_scancode != SDL_SCANCODE_UNKNOWN && p->keys[left_scancode]) {
        p->vx = -MOVE_SPEED;
    }
    if (right_scancode != SDL_SCANCODE_UNKNOWN && p->keys[right_scancode]) {
        p->vx = MOVE_SPEED;
    }
    
    // Jumping (
    if (jump_scancode != SDL_SCANCODE_UNKNOWN && 
        p->keys[jump_scancode] && p->isgrounded) {
        p->vy = -JUMP_FORCE;
        p->isgrounded = false;
        p->isjumping = true;
    }
}

static void plrGravity(Player* p, float dtime) {
    if (!p->isgrounded) {
        p->vy += GRAVITY * dtime;
    }
}
void player_upd(Player* p, float dtime, Level* level) {  // Add level parameter
    plrInput(p);
    plrGravity(p, dtime);

    // Save original position for collision resolution
    float original_x = p->x;
    float original_y = p->y;

    // Apply velocity
    p->x += p->vx * dtime;
    p->y += p->vy * dtime;

    // Check and resolve collisions
    if (level) {
        level_resolve_collision(level, p);
    }

    // Update grounded state
    if (level && player_is_grounded(level, p)) {
        p->isgrounded = 1;
        p->isjumping = 0;
    } else {
        p->isgrounded = 0;
    }

    // Screen boundaries (fallback if no level)
    if (!level) {
        if (p->y > 500 - p->h) {
            p->y = 500 - p->h;
            p->vy = 0;
            p->isgrounded = 1;
            p->isjumping = 0;
        }
        if (p->x < 0) p->x = 0;
        if (p->x > 800 - p->w) p->x = 800 - p->w;
    }
}

void plrRender(Player* p, SDL_Renderer* renderer) {
    // Draw player 
    SDL_SetRenderDrawColor(renderer, p->color.r, p->color.g, p->color.b, 255);
    SDL_RenderFillRect(renderer, &(SDL_FRect){p->x, p->y, p->w, p->h});
    
    // Draw eye
    SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
    float eye_x = p->x + (p->vx >= 0 ? p->w - 10 : 2);
    SDL_RenderFillRect(renderer, &(SDL_FRect){eye_x, p->y + 10, 6, 6});
}
