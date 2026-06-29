#!/usr/bin/env bash
# flash.sh [step_ms] -- build + no-touch-flash the timecode at a chosen step period.
#
#   ./flash.sh         production: tau = 0.5 ms  (camera speed; too fast to see by eye)
#   ./flash.sh 500     demo:       tau = 500 ms  (watchable -- Gray code flips ONE LED per
#                                  step, so all 7 visibly cycle over ~30 s; for showing
#                                  people, or confirming every LED works)
#
# No button needed: the running firmware exposes the USB reset interface, so picotool
# reboots it to BOOTSEL over USB, loads, and runs. STEP_US is a build-time override
# (see CMakeLists.txt). Requires the xpack arm-none-eabi toolchain + pico-sdk + picotool.
set -euo pipefail
step_ms="${1:-0.5}"
step_us=$(python3 -c "import sys; print(round(float(sys.argv[1]) * 1000))" "$step_ms")

export PATH="$HOME/pico/toolchain/xpack-arm-none-eabi-gcc-15.2.1-1.1/bin:$PATH"
export PICO_SDK_PATH="$HOME/pico-sdk"

dir="$(cd "$(dirname "$0")" && pwd)"
[ -f "$dir/pico_sdk_import.cmake" ] || cp "$PICO_SDK_PATH/external/pico_sdk_import.cmake" "$dir/"
mkdir -p "$dir/build" && cd "$dir/build"
cmake -DSTEP_US="$step_us" .. >/dev/null
make -j4 >/dev/null
picotool load -fx timecode.uf2
echo "flashed: tau = ${step_ms} ms (${step_us} us)"
