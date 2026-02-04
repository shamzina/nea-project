#ifndef LEVEL_H
#define LEVEL_H

#include <SDL3/SDL.h>

#define MAX_LEVEL_WIDTH 100
#define MAX_LEVEL_HEIGHT 50
#define TILE_SIZE 32

// Tile types
typedef enum {
    TILE_EMPTY = 0,
    TILE_PLATFORM,
    TILE_P1_SPAWN,
    TILE_P2_SPAWN,
    TILE_GOAL,
    TILE_COUNT
} TileType;

// Level structure
typedef struct {
    int width, height;
    int tiles[MAX_LEVEL_HEIGHT][MAX_LEVEL_WIDTH];
    SDL_FPoint p1_spawn;
    SDL_FPoint p2_spawn;
    SDL_FPoint goal_pos;
    char* filename;
} Level;

// Level functions
int level_load(Level* level, const char* filename);
void level_unload(Level* level);
void level_render(Level* level, SDL_Renderer* renderer);
int level_get_tile(Level* level, int x, int y);
SDL_Color level_get_tile_color(TileType type);

// Utility functions
int level_world_to_tile_x(float world_x);
int level_world_to_tile_y(float world_y);
float level_tile_to_world_x(int tile_x);
float level_tile_to_world_y(int tile_y);

#endif // LEVEL_H