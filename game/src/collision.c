#include "collision.h"
#include "player.h"
#include "level.h"
#include <math.h>

// Check if a rectangle collides with any solid tile
int level_check_collision(Level* level, SDL_FRect rect) {
    // Convert rectangle corners to tile coordinates
    int left_tile = level_world_to_tile_x(rect.x);
    int right_tile = level_world_to_tile_x(rect.x + rect.w - 1);
    int top_tile = level_world_to_tile_y(rect.y);
    int bottom_tile = level_world_to_tile_y(rect.y + rect.h - 1);
    
    // Check all tiles the rectangle touches
    for (int y = top_tile; y <= bottom_tile; y++) {
        for (int x = left_tile; x <= right_tile; x++) {
            TileType tile = level_get_tile(level, x, y);
            if (tile == TILE_PLATFORM) {
                return 1;  // Collision detected
            }
        }
    }
    
    return 0;  // No collision
}

// Resolve collision and adjust player position
void level_resolve_collision(Level* level, Player* player) {
    SDL_FRect player_rect = {player->x, player->y, player->w, player->h};
    
    // Check collision from previous frame
    if (!level_check_collision(level, player_rect)) {
        player->isgrounded = 0;
        return;
    }
    
    // Try moving player out of collision in different directions
    float original_x = player->x;
    float original_y = player->y;
    
    // 1. Check vertical collision (falling/rising)
    player_rect.y = original_y + player->vy * 0.016f;  // Next frame position
    
    if (level_check_collision(level, player_rect)) {
        if (player->vy > 0) {
            // Falling -> Hit ground
            // Find the exact ground position by checking from bottom up
            int bottom_tile = level_world_to_tile_y(original_y + player->h);
            float ground_y = level_tile_to_world_y(bottom_tile) - player->h;
            
            player->y = ground_y;
            player->vy = 0;
            player->isgrounded = 1;
            player->isjumping = 0;
            
        } else if (player->vy < 0) {
            // Rising -> Hit ceiling
            int top_tile = level_world_to_tile_y(original_y) + 1;
            float ceiling_y = level_tile_to_world_y(top_tile);
            
            player->y = ceiling_y;
            player->vy = 0;
        }
    }
    
    // 2. Check horizontal collision (left/right movement)
    player_rect.x = original_x + player->vx * 0.016f;
    player_rect.y = original_y;  // Reset Y to test horizontal only
    
    if (level_check_collision(level, player_rect)) {
        if (player->vx > 0) {
            // Moving right -> Hit right wall
            int right_tile = level_world_to_tile_x(original_x + player->w);
            float wall_x = level_tile_to_world_x(right_tile) - player->w;
            
            player->x = wall_x;
            player->vx = 0;
            
        } else if (player->vx < 0) {
            // Moving left -> Hit left wall
            int left_tile = level_world_to_tile_x(original_x);
            float wall_x = level_tile_to_world_x(left_tile + 1);
            
            player->x = wall_x;
            player->vx = 0;
        }
    }
}

// Check if player is standing on ground
int player_is_grounded(Level* level, Player* player) {
    // Create a small sensor just below player's feet
    SDL_FRect feet_sensor = {
        player->x + 2,                    // Slightly inset from edges
        player->y + player->h,           // Just below player
        player->w - 4,                   // Narrower than player
        2                                // Very thin
    };
    
    return level_check_collision(level, feet_sensor);
}

// Check if player is touching ceiling
int player_is_ceiling(Level* level, Player* player) {
    SDL_FRect head_sensor = {
        player->x + 2,
        player->y - 2,                   // Just above player
        player->w - 4,
        2
    };
    
    return level_check_collision(level, head_sensor);
}

// Check if player reached goal
int player_reached_goal(Level* level, Player* player) {
    SDL_FRect player_rect = {player->x, player->y, player->w, player->h};
    
    // Check all tiles player touches
    int left_tile = level_world_to_tile_x(player->x);
    int right_tile = level_world_to_tile_x(player->x + player->w - 1);
    int top_tile = level_world_to_tile_y(player->y);
    int bottom_tile = level_world_to_tile_y(player->y + player->h - 1);
    
    for (int y = top_tile; y <= bottom_tile; y++) {
        for (int x = left_tile; x <= right_tile; x++) {
            if (level_get_tile(level, x, y) == TILE_GOAL) {
                return 1;
            }
        }
    }
    
    return 0;
}