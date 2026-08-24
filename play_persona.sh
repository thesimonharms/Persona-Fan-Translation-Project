#!/bin/bash
# play_persona.sh - Launcher for Megami Ibunroku Persona (English Fan Translation)
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${PROJECT_DIR}/build"
CUE_FILE="${BUILD_DIR}/Megami_Ibunroku_Persona_EN.cue"
BIN_FILE="${BUILD_DIR}/Megami_Ibunroku_Persona_EN.bin"
LOG_FILE="${BUILD_DIR}/retroarch_last.log"
LAUNCH_CFG="${BUILD_DIR}/retroarch_launch.cfg"
PID_FILE="${BUILD_DIR}/retroarch.pid"

CANDIDATE_CORES=(
    "/usr/lib/libretro/swanstation_libretro.so"
    "/usr/lib/libretro/duckstation_libretro.so"
    "${HOME}/.config/retroarch/cores/swanstation_libretro.so"
    "${HOME}/.config/retroarch/cores/mednafen_psx_hw_libretro.so"
    "${HOME}/.config/retroarch/cores/pcsx_rearmed_libretro.so"
)

usage() {
    cat <<EOF
Usage: $0 [--kill] [--help]
  --kill   Stop leftover Persona RetroArch (SIGTERM, then SIGKILL)
EOF
}

persona_ra_pids() {
    local pid cmd
    # Only the retroarch binary. Never match this script or a diagnostic command.
    while read -r pid; do
        [ -n "${pid}" ] || continue
        cmd=$(tr '\0' ' ' < "/proc/${pid}/cmdline" 2>/dev/null || true)
        case "${cmd}" in
            *Megami_Ibunroku_Persona_EN*) printf '%s\n' "${pid}" ;;
        esac
    done < <(pgrep -x retroarch || true)
    if [ -f "${PID_FILE}" ]; then
        pid=$(cat "${PID_FILE}")
        if [ -n "${pid}" ] && [ -r "/proc/${pid}/comm" ] \
            && [ "$(cat "/proc/${pid}/comm")" = retroarch ]; then
            printf '%s\n' "${pid}"
        fi
    fi
}

kill_persona_ra() {
    local pids seen="" any=0 pid
    mapfile -t pids < <(persona_ra_pids | awk 'NF && !seen[$0]++')
    for pid in "${pids[@]}"; do
        [ -n "${pid}" ] || continue
        if kill -0 "${pid}" 2>/dev/null; then
            any=1
            echo "[*] Stopping RetroArch pid ${pid}"
            kill -TERM "${pid}" 2>/dev/null || true
        fi
    done
    if [ "${any}" -eq 0 ]; then
        echo "[*] No Persona RetroArch process found."
        rm -f "${PID_FILE}"
        return 0
    fi
    sleep 1
    for pid in "${pids[@]}"; do
        if kill -0 "${pid}" 2>/dev/null; then
            echo "[*] SIGKILL pid ${pid}"
            kill -KILL "${pid}" 2>/dev/null || true
        fi
    done
    rm -f "${PID_FILE}"
    echo "[+] RetroArch stopped."
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    usage
    exit 0
fi
if [ "${1:-}" = "--kill" ]; then
    kill_persona_ra
    exit 0
fi

SELECTED_CORE=""
for core_path in "${CANDIDATE_CORES[@]}"; do
    if [ -f "${core_path}" ]; then
        SELECTED_CORE="${core_path}"
        break
    fi
done

if [ ! -f "${CUE_FILE}" ] || [ ! -f "${BIN_FILE}" ]; then
    echo "[!] Translated disc image not found. Building disc image first..."
    python3 "${PROJECT_DIR}/tools/rebuilder.py"
fi
if [ ! -f "${CUE_FILE}" ] || [ ! -f "${BIN_FILE}" ]; then
    echo "[!] Still missing ${CUE_FILE} or ${BIN_FILE}" >&2
    exit 1
fi

if [ -n "$(persona_ra_pids)" ]; then
    echo "[!] Leftover RetroArch is still running. Stopping it first..."
    kill_persona_ra
fi

# CUE FILE name is relative to this directory.
cd "${BUILD_DIR}"

# SDL2 creates a real Hyprland window. The default gl/wayland path here
# reports "display server: null", grabs the TTY, and can hang with no window.
cat > "${LAUNCH_CFG}" <<'EOF'
log_verbosity = "true"
pause_nonactive = "false"
video_fullscreen = "false"
video_windowed_fullscreen = "false"
video_window_show_decorations = "true"
video_driver = "sdl2"
input_driver = "sdl2"
video_context_driver = ""
config_save_on_exit = "false"
notification_show_autoconfig = "false"
EOF

RA_ARGS=(
    -v
    --log-file="${LOG_FILE}"
    --appendconfig="${LAUNCH_CFG}"
)
if [ -n "${SELECTED_CORE}" ]; then
    RA_ARGS+=(-L "${SELECTED_CORE}")
    echo "[*] Core: ${SELECTED_CORE}"
fi
RA_ARGS+=("${CUE_FILE}")

echo "[*] Disc: ${CUE_FILE}"
echo "[*] Log : ${LOG_FILE}"

# Detached so this terminal stays usable. Ctrl+C will not be swallowed.
setsid retroarch "${RA_ARGS[@]}" </dev/null >/dev/null 2>&1 &
RA_PID=$!
echo "${RA_PID}" > "${PID_FILE}"
echo "[*] PID : ${RA_PID}"

for _ in 1 2 3 4 5 6 7 8; do
    if ! kill -0 "${RA_PID}" 2>/dev/null; then
        echo "[!] RetroArch exited immediately. Last log lines:" >&2
        tail -30 "${LOG_FILE}" >&2 || true
        rm -f "${PID_FILE}"
        exit 1
    fi
    if hyprctl clients 2>/dev/null | grep -q "pid: ${RA_PID}"; then
        echo "[+] Window is up (class com.libretro.RetroArch)."
        echo "[*] Quit: Esc in the game window, or  ./play_persona.sh --kill"
        exit 0
    fi
    sleep 1
done

echo "[!] RetroArch is running (pid ${RA_PID}) but Hyprland has no window yet."
echo "    Check ${LOG_FILE}"
echo "    Kill with: ./play_persona.sh --kill"
exit 0
