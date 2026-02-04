#ifndef COLLISION_H
#define COLLISION_H

#include <SDL3/SDL.h>
#include "level.h"
#include "player.h"

// Collision detection
int level_check_collision(Level* level, SDL_FRect rect);
void level_resolve_collision(Level* level, Player* player);

// Player state checks
int player_is_grounded(Level* level, Player* player);
int player_is_ceiling(Level* level, Player* player);
int player_reached_goal(Level* level, Player* player);

#endif // COLLISION_H