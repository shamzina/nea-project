#include "game.h"
#include <stdio.h>

int main(int argc, char* argv[]) {
    printf("Starting Tethered Together...\n");

    Game game;  // Changed from GameState to Game

    if (!game_init(&game)) {
        printf("Game initialization failed!\n");
        return 1;
    }

    printf("Running game loop...\n");
    game_run(&game);

    printf("Cleaning up...\n");
    game_cleanup(&game);  // Changed from cleanup to game_cleanup

    printf("Game exited successfully.\n");
    return 0;
}
