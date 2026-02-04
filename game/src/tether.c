#include "tether.h"
#include <math.h>
#include <stdio.h>

// Initialize tether with default values
void tether_init(Tether* tether, float max_length) {
    tether->max_length = max_length;
    tether->stiffness = TETHER_STIFFNESS;
    tether->damping = TETHER_DAMPING;
    tether->color = (SDL_Color){255, 255, 255, 255};  // White
    tether->is_active = 1;
    printf("Tether initialized: max length = %.0fpx\n", max_length);
}

// Calculate current distance between players
float tether_get_current_length(Player* p1, Player* p2) {
    float dx = p2->x - p1->x;
    float dy = p2->y - p1->y;
    return sqrtf(dx*dx + dy*dy);
}

// Check if tether is stretched beyond max length
int tether_is_stretched(Player* p1, Player* p2, float max_length) {
    float distance = tether_get_current_length(p1, p2);
    return (distance > max_length);
}

// Apply tether physics to players
void tether_update(Tether* tether, Player* p1, Player* p2, float delta_time) {
    if (!tether->is_active) return;

    float dx = p2->x - p1->x;
    float dy = p2->y - p1->y;
    float distance = sqrtf(dx*dx + dy*dy);

    // If within max length, no force needed
    if (distance <= tether->max_length || distance < 1.0f) {
        return;
    }

    // Normalize direction vector
    float inv_distance = 1.0f / distance;
    float dir_x = dx * inv_distance;
    float dir_y = dy * inv_distance;

    // Calculate stretch (how much beyond max length)
    float stretch = distance - tether->max_length;

    // Spring force: F = k * stretch
    float force_magnitude = tether->stiffness * stretch;

    // Apply damping to velocities (reduce oscillation)
    p1->vx *= tether->damping;
    p1->vy *= tether->damping;
    p2->vx *= tether->damping;
    p2->vy *= tether->damping;

    // Apply forces to both players (equal and opposite)
    // Player 1 gets pulled toward Player 2
    p1->vx += force_magnitude * dir_x * delta_time;
    p1->vy += force_magnitude * dir_y * delta_time;

    // Player 2 gets pulled toward Player 1
    p2->vx -= force_magnitude * dir_x * delta_time;
    p2->vy -= force_magnitude * dir_y * delta_time;

    // Optional: Direct position correction for tight control
    if (stretch > 10.0f) {  // Only if severely stretched
        float correction = stretch * 0.5f;  // Move halfway back

        // Move players toward each other
        p1->x += correction * dir_x;
        p1->y += correction * dir_y;
        p2->x -= correction * dir_x;
        p2->y -= correction * dir_y;
    }
}

// Render the tether as a line between players
void tether_render(Tether* tether, Player* p1, Player* p2, SDL_Renderer* renderer) {
    if (!tether->is_active) return;

    // Calculate center points of players
    float p1_center_x = p1->x + p1->w / 2;
    float p1_center_y = p1->y + p1->h / 2;
    float p2_center_x = p2->x + p2->w / 2;
    float p2_center_y = p2->y + p2->h / 2;

    // Calculate distance for color effect
    float distance = tether_get_current_length(p1, p2);
    float stretch_ratio = distance / tether->max_length;

    // Change color based on tension (white -> yellow -> red)
    SDL_Color color;
    if (stretch_ratio < 0.8f) {
        color = (SDL_Color){255, 255, 255, 255};  // White (loose)
    } else if (stretch_ratio < 1.0f) {
        color = (SDL_Color){255, 255, 100, 255};  // Yellow (tight)
    } else {
        color = (SDL_Color){255, 100, 100, 255};  // Red (overstretched)
    }

    // Draw the tether line
    SDL_SetRenderDrawColor(renderer, color.r, color.g, color.b, 255);

    // Draw multiple lines for thickness
    for (int i = 0; i < TETHER_THICKNESS; i++) {
        float offset = i - TETHER_THICKNESS / 2.0f;
        SDL_RenderLine(renderer,
                      p1_center_x + offset, p1_center_y + offset,
                      p2_center_x + offset, p2_center_y + offset);
    }

    // Draw tether length indicator (optional debug)
    if (distance > tether->max_length * 0.9f) {
        // Draw warning indicator
        float mid_x = (p1_center_x + p2_center_x) / 2;
        float mid_y = (p1_center_y + p2_center_y) / 2;

        SDL_SetRenderDrawColor(renderer, 255, 50, 50, 255);
        SDL_RenderRect(renderer, &(SDL_FRect){mid_x - 5, mid_y - 5, 10, 10});
    }
}
