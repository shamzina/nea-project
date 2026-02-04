#ifndef TETHER_H
#define TETHER_H

#include <SDL3/SDL.h>
#include "player.h"

#define MAX_TETHER_LENGTH 300.0f  // Maximum distance in pixels
#define TETHER_STIFFNESS 500.0f   // Spring constant
#define TETHER_DAMPING 0.8f       // Damping factor (0-1)
#define TETHER_THICKNESS 3.0f     // Visual thickness

typedef struct {
    float max_length;
    float stiffness;
    float damping;
    SDL_Color color;
    int is_active;
} Tether;

// Tether functions
void tether_init(Tether* tether, float max_length);
void tether_update(Tether* tether, Player* p1, Player* p2, float delta_time);
void tether_render(Tether* tether, Player* p1, Player* p2, SDL_Renderer* renderer);
float tether_get_current_length(Player* p1, Player* p2);
int tether_is_stretched(Player* p1, Player* p2, float max_length);

#endif // TETHER_H
