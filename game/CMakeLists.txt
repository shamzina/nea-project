cmake_minimum_required(VERSION 3.20)
project(TetheredTogether C)

set(CMAKE_C_STANDARD 11)

# Find SDL3
find_package(SDL3 REQUIRED)
#find_package(SDL3_image REQUIRED)
#find_package(SDL3_ttf REQUIRED)

file(MAKE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/assets/levels)

configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/assets/levels/level1.txt
    ${CMAKE_CURRENT_BINARY_DIR}/level1.txt
    COPYONLY
)

# src files
set(SOURCES 
    src/main.c 
    src/game.c 
    src/player.c
    src/level.c
    src/collision.c
    src/tether.c
)

# header files
set(HEADERS 
    inc/game.h 
    inc/player.h
    inc/level.h
    inc/collision.h
    inc/tether.h
)

# create executable
add_executable(tethered_together ${SOURCES} ${HEADERS})

# include dir
target_include_directories(tethered_together PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/inc 
    ${SDL3_INCLUDE_DIRS}
)

# link libraries
target_link_libraries(tethered_together
    SDL3::SDL3
    #SDL3::SDL3_image
    #SDL3::SDL3_ttf
    m
)

