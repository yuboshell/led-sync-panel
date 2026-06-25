cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)        # copy this from pico-sdk/external/ (gitignored — SDK file)
project(blink C CXX ASM)
set(CMAKE_C_STANDARD 11)
pico_sdk_init()
add_executable(blink main.c)
target_link_libraries(blink pico_stdlib)
pico_add_extra_outputs(blink)        # produces blink.uf2
