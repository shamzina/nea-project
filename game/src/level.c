#include "level.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

int level_load(Level* level, const char* filename) {
    printf("Loading level: %s\n", filename);
    
    FILE* file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Failed to open level file: %s\n", filename);
        return 0;
    }
    
    // Initialize level
    memset(level, 0, sizeof(Level));
    level->filename = strdup(filename);
    
    char line[256];
    int line_num = 0;
    int reading_map = 0;
    int row = 0;
    
    while (fgets(line, sizeof(line), file)) {
        line_num++;
        
        // Remove trailing newline
        line[strcspn(line, "\n")] = 0;
        
        // Skip empty lines and comments
        if (line[0] == '#' || line[0] == '\0') {
            continue;
        }
        
        if (!reading_map) {
            // Read header data
            if (level->width == 0) {
                // First non-comment line: width height
                sscanf(line, "%d %d", &level->width, &level->height);
                
                if (level->width > MAX_LEVEL_WIDTH || level->height > MAX_LEVEL_HEIGHT) {
                    fprintf(stderr, "Level too large: %dx%d (max: %dx%d)\n", 
                            level->width, level->height, 
                            MAX_LEVEL_WIDTH, MAX_LEVEL_HEIGHT);
                    fclose(file);
                    return 0;
                }
                
                printf("Level size: %dx%d tiles\n", level->width, level->height);
                
            } else if (level->p1_spawn.x == 0) {
                // Second: player 1 spawn
                sscanf(line, "%f %f", &level->p1_spawn.x, &level->p1_spawn.y);
                printf("P1 spawn: %.0f,%.0f\n", level->p1_spawn.x, level->p1_spawn.y);
                
            } else if (level->p2_spawn.x == 0) {
                // Third: player 2 spawn
                sscanf(line, "%f %f", &level->p2_spawn.x, &level->p2_spawn.y);
                printf("P2 spawn: %.0f,%.0f\n", level->p2_spawn.x, level->p2_spawn.y);
                
            } else if (level->goal_pos.x == 0) {
                // Fourth: goal position
                sscanf(line, "%f %f", &level->goal_pos.x, &level->goal_pos.y);
                printf("Goal: %.0f,%.0f\n", level->goal_pos.x, level->goal_pos.y);
                
                reading_map = 1;  // Start reading tile map
                printf("Reading tile map...\n");
            }
            
        } else {
            // Reading tile map
            if (row >= level->height) {
                fprintf(stderr, "Too many rows in tile map\n");
                break;
            }
            
            // Parse each character as a tile
            for (int col = 0; col < level->width && line[col] != '\0'; col++) {
                char c = line[col];
                int tile = c - '0';  // Convert char '0'-'9' to int 0-9
                
                if (tile >= 0 && tile < TILE_COUNT) {
                    level->tiles[row][col] = tile;
                } else {
                    level->tiles[row][col] = TILE_EMPTY;
                }
            }
            
            row++;
        }
    }
    
    fclose(file);
    
    if (row != level->height) {
        fprintf(stderr, "Warning: Expected %d rows, got %d\n", level->height, row);
    }
    
    printf("Level loaded successfully: %s\n", filename);
    return 1;
}

void level_unload(Level* level) {
    if (level->filename) {
        free(level->filename);
        level->filename = NULL;
    }
    printf("Level unloaded\n");
}

int level_get_tile(Level* level, int tile_x, int tile_y) {
    if (tile_x < 0 || tile_x >= level->width || 
        tile_y < 0 || tile_y >= level->height) {
        return TILE_PLATFORM;  // Treat out-of-bounds as solid
    }
    return level->tiles[tile_y][tile_x];
}

SDL_Color level_get_tile_color(TileType type) {
    switch (type) {
        case TILE_PLATFORM:
            return (SDL_Color){120, 120, 120, 255};  // Gray
        case TILE_P1_SPAWN:
            return (SDL_Color){219, 68, 85, 100};    // Red (transparent)
        case TILE_P2_SPAWN:
            return (SDL_Color){72, 133, 237, 100};   // Blue (transparent)
        case TILE_GOAL:
            return (SDL_Color){97, 189, 109, 255};   // Green
        default:
            return (SDL_Color){0, 0, 0, 0};          // Transparent
    }
}

void level_render(Level* level, SDL_Renderer* renderer) {
    for (int y = 0; y < level->height; y++) {
        for (int x = 0; x < level->width; x++) {
            TileType tile = level->tiles[y][x];
            
            if (tile == TILE_EMPTY) {
                continue;  // Don't render empty tiles
            }
            
            SDL_Color color = level_get_tile_color(tile);
            SDL_SetRenderDrawColor(renderer, color.r, color.g, color.b, color.a);
            
            SDL_FRect tile_rect = {
                x * TILE_SIZE,
                y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            };
            
            SDL_RenderFillRect(renderer, &tile_rect);
            
            // Add grid lines for platforms
            if (tile == TILE_PLATFORM) {
                SDL_SetRenderDrawColor(renderer, 80, 80, 80, 255);
                SDL_RenderRect(renderer, &tile_rect);
            }
        }
    }
}

// Coordinate conversion utilities
int level_world_to_tile_x(float world_x) {
    return (int)(world_x / TILE_SIZE);
}

int level_world_to_tile_y(float world_y) {
    return (int)(world_y / TILE_SIZE);
}

float level_tile_to_world_x(int tile_x) {
    return tile_x * TILE_SIZE;
}

float level_tile_to_world_y(int tile_y) {
    return tile_y * TILE_SIZE;
}