cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)        # copy from pico-sdk/external/ (gitignored — SDK file)
project(timecode C CXX ASM)
set(CMAKE_C_STANDARD 11)
pico_sdk_init()
add_executable(timecode main.c)
if(DEFINED STEP_US)                   # demo/diagnostic override: cmake -DSTEP_US=<microseconds> (see flash.sh)
    target_compile_definitions(timecode PRIVATE STEP_US=${STEP_US}u)
endif()
target_link_libraries(timecode pico_stdlib hardware_spi)
pico_enable_stdio_usb(timecode 1)     # USB CDC + reset interface -> picotool can reboot to BOOTSEL over USB
pico_enable_stdio_uart(timecode 0)    # (no-touch reflashing after the first load: picotool load -fx)
pico_add_extra_outputs(timecode)      # produces timecode.uf2
