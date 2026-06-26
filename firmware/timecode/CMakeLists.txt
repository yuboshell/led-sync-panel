cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)        # copy from pico-sdk/external/ (gitignored — SDK file)
project(timecode C CXX ASM)
set(CMAKE_C_STANDARD 11)
pico_sdk_init()
add_executable(timecode main.c)
target_link_libraries(timecode pico_stdlib hardware_spi)
pico_add_extra_outputs(timecode)      # produces timecode.uf2
