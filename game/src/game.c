#include "game.h"
#include <string.h>

// Global constants
static const char* TITLE = "Tethered Together";
static const int WIDTH = 800, HEIGHT = 600;

// Forward declarations for INTERNAL functions
static int init_sdl(Game* game);
static void handle_events(Game* game);
static void update(Game* game);
static void render(Game* game);
static float get_delta_time(Game* game);
static void create_default_level(Level* level);
static void reset_game(Game* game);

// UI functions (internal to game.c)
static void ui_init_buttons(Game* game);
static void ui_update_buttons(Game* game);
static void ui_render_buttons(Game* game);
static void ui_render_hud(Game* game);

int game_init(Game* game) {
    printf("Initializing game...\n");

    // Initialize game state
    memset(game, 0, sizeof(Game));
    game->current_state = STATE_MENU;
    game->run = true;
    game->perf_freq = SDL_GetPerformanceFrequency();
    game->lftime = SDL_GetPerformanceCounter();
    game->current_level_index = 1;
    game->attempts = 1;

    // Initialize SDL
    if (!init_sdl(game)) {
        fprintf(stderr, "SDL initialization failed!\n");
        return 0;
    }

    // Initialize UI
    ui_init_buttons(game);

    printf("Game initialized successfully\n");
    return 1;
}

// Initialize menu buttons
static void ui_init_buttons(Game* game) {
    float center_x = 400;
    float button_width = 200;
    float button_height = 50;
    float start_y = 200;
    float spacing = 70;

    // Play button
    game->menu_buttons[0].rect = (SDL_FRect){center_x - button_width/2, start_y, button_width, button_height};
    snprintf(game->menu_buttons[0].text, 50, "PLAY");
    game->menu_buttons[0].normal_color = (SDL_Color){100, 150, 255, 255};
    game->menu_buttons[0].hover_color = (SDL_Color){150, 200, 255, 255};

    // Quit button
    game->menu_buttons[1].rect = (SDL_FRect){center_x - button_width/2, start_y + spacing, button_width, button_height};
    snprintf(game->menu_buttons[1].text, 50, "QUIT");
    game->menu_buttons[1].normal_color = (SDL_Color){255, 100, 100, 255};
    game->menu_buttons[1].hover_color = (SDL_Color){255, 150, 150, 255};

    for (int i = 0; i < 2; i++) {
        game->menu_buttons[i].is_hovered = 0;
        game->menu_buttons[i].is_clicked = 0;
    }
}

// Update button states
static void ui_update_buttons(Game* game) {
    float mouse_x, mouse_y;
    SDL_GetMouseState(&mouse_x, &mouse_y);

    for (int i = 0; i < 2; i++) {
        Button* btn = &game->menu_buttons[i];
        btn->is_hovered = (mouse_x >= btn->rect.x &&
        mouse_x <= btn->rect.x + btn->rect.w &&
        mouse_y >= btn->rect.y &&
        mouse_y <= btn->rect.y + btn->rect.h);
    }
}

// Render buttons
static void ui_render_buttons(Game* game) {
    for (int i = 0; i < 2; i++) {
        Button* btn = &game->menu_buttons[i];
        SDL_Color color = btn->is_hovered ? btn->hover_color : btn->normal_color;

        // Draw button
        SDL_SetRenderDrawColor(game->renderer, color.r, color.g, color.b, 200);
        SDL_RenderFillRect(game->renderer, &btn->rect);

        // Draw border
        SDL_SetRenderDrawColor(game->renderer, 255, 255, 255, 255);
        SDL_RenderRect(game->renderer, &btn->rect);

        // Simple text placeholder (rectangle)
        float text_width = strlen(btn->text) * 10;
        SDL_FRect text_bg = {
            btn->rect.x + btn->rect.w/2 - text_width/2,
            btn->rect.y + btn->rect.h/2 - 8,
            text_width,
            16
        };
        SDL_SetRenderDrawColor(game->renderer, 255, 255, 255, 255);
        SDL_RenderFillRect(game->renderer, &text_bg);
    }
}

// Render HUD
static void ui_render_hud(Game* game) {
    // Top bar
    SDL_SetRenderDrawColor(game->renderer, 0, 0, 0, 180);
    SDL_RenderFillRect(game->renderer, &(SDL_FRect){0, 0, 800, 40});

    // Tether meter
    float distance = tether_get_current_length(&game->player1, &game->player2);
    float max_length = game->tether.max_length;

    SDL_SetRenderDrawColor(game->renderer, 100, 100, 100, 255);
    SDL_RenderRect(game->renderer, &(SDL_FRect){10, 15, 200, 10});

    SDL_Color meter_color;
    if (distance < max_length * 0.7f) {
        meter_color = (SDL_Color){100, 255, 100, 255};
    } else if (distance < max_length) {
        meter_color = (SDL_Color){255, 255, 100, 255};
    } else {
        meter_color = (SDL_Color){255, 100, 100, 255};
    }

    SDL_SetRenderDrawColor(game->renderer, meter_color.r, meter_color.g, meter_color.b, 255);
    float fill_width = (distance > max_length ? 200 : distance/max_length * 200);
    SDL_RenderFillRect(game->renderer, &(SDL_FRect){12, 17, fill_width - 4, 6});

    // Time display
    int minutes = (int)game->game_time / 60;
    int seconds = (int)game->game_time % 60;
    SDL_SetRenderDrawColor(game->renderer, 255, 255, 255, 255);
    SDL_RenderFillRect(game->renderer, &(SDL_FRect){650, 10, 140, 20});
    SDL_SetRenderDrawColor(game->renderer, 0, 0, 0, 255);
    SDL_RenderRect(game->renderer, &(SDL_FRect){650, 10, 140, 20});
}

// Initialize SDL
static int init_sdl(Game* game) {
    if (!SDL_Init(SDL_INIT_VIDEO)) {
        fprintf(stderr, "SDL_Init Error: %s\n", SDL_GetError());
        return 0;
    }

    game->window = SDL_CreateWindow(TITLE, WIDTH, HEIGHT, 0);
    if (!game->window) {
        fprintf(stderr, "SDL_CreateWindow Error: %s\n", SDL_GetError());
        SDL_Quit();
        return 0;
    }

    game->renderer = SDL_CreateRenderer(game->window, NULL);
    if (!game->renderer) {
        fprintf(stderr, "SDL_CreateRenderer Error: %s\n", SDL_GetError());
        SDL_DestroyWindow(game->window);
        SDL_Quit();
        return 0;
    }

    return 1;
}

// Create default level if file missing
static void create_default_level(Level* level) {
    printf("Creating default level...\n");

    level->width = 25;
    level->height = 15;
    level->p1_spawn = (SDL_FPoint){22, 10};
    level->p2_spawn = (SDL_FPoint){22, 10};
    level->goal_pos = (SDL_FPoint){12, 5};

    for (int y = 0; y < level->height; y++) {
        for (int x = 0; x < level->width; x++) {
            if (x == 0 || x == level->width - 1 || y == level->height - 1 || y == 0) {
                level->tiles[y][x] = TILE_PLATFORM;
            } else if (y == 10 && (x >= 5 && x <= 8 || x >= 17 && x <= 20)) {
                level->tiles[y][x] = TILE_PLATFORM;
            } else if (x == (int)level->goal_pos.x && y == (int)level->goal_pos.y) {
                level->tiles[y][x] = TILE_GOAL;
            } else {
                level->tiles[y][x] = TILE_EMPTY;
            }
        }
    }

    level->tiles[(int)level->p1_spawn.y][(int)level->p1_spawn.x] = TILE_P1_SPAWN;
    level->tiles[(int)level->p2_spawn.y][(int)level->p2_spawn.x] = TILE_P2_SPAWN;
}

// Reset game to initial state
static void reset_game(Game* game) {
    printf("Resetting game...\n");

    // Load level
    char level_path[100];
    snprintf(level_path, sizeof(level_path), "assets/levels/level%d.txt", game->current_level_index);

    if (!level_load(&game->current_level, level_path)) {
        fprintf(stderr, "Failed to load level %d! Using default...\n", game->current_level_index);
        create_default_level(&game->current_level);
    }

    // Reset players
    initPlayer(&game->player1,
               game->current_level.p1_spawn.x * TILE_SIZE,
               game->current_level.p1_spawn.y * TILE_SIZE,
               SDLK_A, SDLK_D, SDLK_W,
               (SDL_Color){219, 68, 85, 255});

    initPlayer(&game->player2,
               game->current_level.p2_spawn.x * TILE_SIZE,
               game->current_level.p2_spawn.y * TILE_SIZE,
               SDLK_LEFT, SDLK_RIGHT, SDLK_UP,
               (SDL_Color){72, 133, 237, 255});

    // Reset tether
    tether_init(&game->tether, MAX_TETHER_LENGTH);

    // Reset timer
    game->game_time = 0;

    printf("Game reset complete\n");
}

// Get delta time
static float get_delta_time(Game* game) {
    Uint64 now = SDL_GetPerformanceCounter();
    float delta = (float)(now - game->lftime) / game->perf_freq;
    game->lftime = now;
    return delta;
}

// Handle events
static void handle_events(Game* game) {
    SDL_Event ev;
    while (SDL_PollEvent(&ev)) {
        switch (ev.type) {
            case SDL_EVENT_QUIT:
                game->run = false;
                break;

            case SDL_EVENT_KEY_DOWN:
                switch (ev.key.key) {
                    case SDLK_ESCAPE:
                        if (game->current_state == STATE_PLAYING) {
                            game->current_state = STATE_PAUSED;
                            printf("Game paused\n");
                        } else if (game->current_state == STATE_PAUSED) {
                            game->current_state = STATE_PLAYING;
                            printf("Game unpaused\n");
                        }
                        break;
                    case SDLK_P:
                        if (game->current_state == STATE_PLAYING) {
                            game->current_state = STATE_PAUSED;
                        } else if (game->current_state == STATE_PAUSED) {
                            game->current_state = STATE_PLAYING;
                        }
                        break;
                }
                break;

                    case SDL_EVENT_MOUSE_BUTTON_DOWN:
                        if (ev.button.button == SDL_BUTTON_LEFT) {
                            // Check menu button clicks
                            if (game->current_state == STATE_MENU) {
                                float mouse_x = ev.button.x;
                                float mouse_y = ev.button.y;

                                for (int i = 0; i < 2; i++) {
                                    Button* btn = &game->menu_buttons[i];
                                    if (mouse_x >= btn->rect.x && mouse_x <= btn->rect.x + btn->rect.w &&
                                        mouse_y >= btn->rect.y && mouse_y <= btn->rect.y + btn->rect.h) {
                                        if (i == 0) { // PLAY
                                            reset_game(game);
                                            game->current_state = STATE_PLAYING;
                                            printf("Starting game...\n");
                                        } else if (i == 1) { // QUIT
                                            game->run = false;
                                            printf("Quitting game...\n");
                                        }
                                        }
                                }
                            }
                        }
                        break;
        }
    }
}

// Update game based on state
static void update(Game* game) {
    switch (game->current_state) {
        case STATE_MENU:
            ui_update_buttons(game);
            break;

        case STATE_PLAYING:
            game->game_time += game->dtime;

            // Gameplay update
            player_upd(&game->player1, game->dtime, &game->current_level);
            player_upd(&game->player2, game->dtime, &game->current_level);
            tether_update(&game->tether, &game->player1, &game->player2, game->dtime);

            // Check for victory
            if (player_reached_goal(&game->current_level, &game->player1) &&
                player_reached_goal(&game->current_level, &game->player2)) {
                printf("Level completed in %.1f seconds!\n", game->game_time);
            game->current_state = STATE_VICTORY;
                }

                // Check for game over
                if (game->player1.y > 600 || game->player2.y > 600) {
                    printf("Players fell! Attempt: %d\n", game->attempts);
                    game->current_state = STATE_GAME_OVER;
                }
                break;

        case STATE_PAUSED:
            // Just wait for unpause
            break;

        case STATE_GAME_OVER:
            // Check for retry or menu
        {
            const bool* keys = SDL_GetKeyboardState(NULL);
            static int debounce = 0;

            if (debounce > 0) debounce--;

            if (keys[SDL_SCANCODE_R] && debounce == 0) {
                game->attempts++;
                reset_game(game);
                game->current_state = STATE_PLAYING;
                debounce = 30;
                printf("Retry attempt %d\n", game->attempts);
            }

            if (keys[SDL_SCANCODE_M] && debounce == 0) {
                game->current_state = STATE_MENU;
                debounce = 30;
                printf("Returning to menu\n");
            }
        }
        break;

        case STATE_VICTORY:
            // Check for next level or menu
        {
            const bool* keys = SDL_GetKeyboardState(NULL);
            static int debounce = 0;

            if (debounce > 0) debounce--;

            if (keys[SDL_SCANCODE_N] && debounce == 0) {
                game->current_level_index++;
                reset_game(game);
                game->current_state = STATE_PLAYING;
                debounce = 30;
                printf("Starting level %d\n", game->current_level_index);
            }

            if (keys[SDL_SCANCODE_M] && debounce == 0) {
                game->current_state = STATE_MENU;
                debounce = 30;
                printf("Returning to menu\n");
            }
        }
        break;
    }
}

// Render based on state
static void render(Game* game) {
    SDL_SetRenderDrawColor(game->renderer, 30, 32, 40, 255);
    SDL_RenderClear(game->renderer);

    switch (game->current_state) {
        case STATE_MENU:
            // Title
            SDL_SetRenderDrawColor(game->renderer, 100, 150, 255, 255);
            SDL_RenderFillRect(game->renderer, &(SDL_FRect){200, 50, 400, 80});

            // Buttons
            ui_render_buttons(game);

            // Instructions
            SDL_SetRenderDrawColor(game->renderer, 200, 200, 200, 255);
            SDL_RenderFillRect(game->renderer, &(SDL_FRect){150, 400, 500, 150});
            break;

        case STATE_PLAYING:
        case STATE_PAUSED:
            // Gameplay
            level_render(&game->current_level, game->renderer);
            tether_render(&game->tether, &game->player1, &game->player2, game->renderer);
            plrRender(&game->player1, game->renderer);
            plrRender(&game->player2, game->renderer);
            ui_render_hud(game);

            // Pause overlay
            if (game->current_state == STATE_PAUSED) {
                SDL_SetRenderDrawColor(game->renderer, 0, 0, 0, 180);
                SDL_RenderFillRect(game->renderer, &(SDL_FRect){0, 0, 800, 600});

                SDL_SetRenderDrawColor(game->renderer, 255, 255, 255, 255);
                SDL_RenderFillRect(game->renderer, &(SDL_FRect){300, 250, 200, 100});
            }
            break;

        case STATE_GAME_OVER:
            // Game in background
            level_render(&game->current_level, game->renderer);
            plrRender(&game->player1, game->renderer);
            plrRender(&game->player2, game->renderer);

            // Overlay
            SDL_SetRenderDrawColor(game->renderer, 0, 0, 0, 200);
            SDL_RenderFillRect(game->renderer, &(SDL_FRect){0, 0, 800, 600});

            SDL_SetRenderDrawColor(game->renderer, 255, 100, 100, 255);
            SDL_RenderFillRect(game->renderer, &(SDL_FRect){200, 150, 400, 100});

            // Instructions
            SDL_SetRenderDrawColor(game->renderer, 255, 255, 255, 255);
            SDL_RenderFillRect(game->renderer, &(SDL_FRect){250, 300, 300, 150});
            break;

        case STATE_VICTORY:
            // Game in background
            level_render(&game->current_level, game->renderer);
            plrRender(&game->player1, game->renderer);
            plrRender(&game->player2, game->renderer);

            // Overlay
            SDL_SetRenderDrawColor(game->renderer, 0, 0, 0, 180);
            SDL_RenderFillRect(game->renderer, &(SDL_FRect){0, 0, 800, 600});

            SDL_SetRenderDrawColor(game->renderer, 100, 255, 100, 255);
            SDL_RenderFillRect(game->renderer, &(SDL_FRect){200, 150, 400, 100});

            // Stats
            SDL_SetRenderDrawColor(game->renderer, 50, 50, 50, 255);
            SDL_RenderFillRect(game->renderer, &(SDL_FRect){250, 300, 300, 150});

            // Continue button
            SDL_SetRenderDrawColor(game->renderer, 100, 150, 255, 255);
            SDL_RenderFillRect(game->renderer, &(SDL_FRect){350, 480, 100, 40});
            break;
    }

    SDL_RenderPresent(game->renderer);
}

// Main game loop
void game_run(Game* game) {
    int frames = 0;
    Uint64 fps_timer = SDL_GetTicks();

    printf("Entering game loop...\n");

    while (game->run) {
        Uint64 frame_start = SDL_GetPerformanceCounter();

        // Update delta time
        game->dtime = get_delta_time(game);

        // Handle events
        handle_events(game);

        // Update
        update(game);

        // Render
        render(game);

        // Frame timing
        Uint64 frame_time = SDL_GetPerformanceCounter() - frame_start;
        float frame_time_ms = (frame_time * 1000.0f) / game->perf_freq;

        if (frame_time_ms < FRAME_TIME_MS) {
            SDL_Delay((Uint32)(FRAME_TIME_MS - frame_time_ms));
        }

        // FPS counter
        frames++;
        if (SDL_GetTicks() - fps_timer >= 1000) {
            float fps = frames / ((SDL_GetTicks() - fps_timer) / 1000.0f);
            printf("FPS: %.1f | State: %d\n", fps, game->current_state);
            frames = 0;
            fps_timer = SDL_GetTicks();
        }
    }
}

// Cleanup
void game_cleanup(Game* game) {
    level_unload(&game->current_level);

    if (game->renderer) {
        SDL_DestroyRenderer(game->renderer);
        game->renderer = NULL;
    }

    if (game->window) {
        SDL_DestroyWindow(game->window);
        game->window = NULL;
    }

    SDL_Quit();
    printf("Cleanup complete\n");
}
