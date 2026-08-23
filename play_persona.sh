#!/bin/bash
# play_persona.sh - Quick launcher for Megami Ibunroku Persona (English Fan Translation)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CUE_FILE="${PROJECT_DIR}/build/Megami_Ibunroku_Persona_EN.cue"

# Candidate core locations (prioritizing AUR system-installed core)
CANDIDATE_CORES=(
    "/usr/lib/libretro/swanstation_libretro.so"
    "/usr/lib/libretro/duckstation_libretro.so"
    "${HOME}/.config/retroarch/cores/swanstation_libretro.so"
    "${HOME}/.config/retroarch/cores/mednafen_psx_hw_libretro.so"
    "${HOME}/.config/retroarch/cores/pcsx_rearmed_libretro.so"
)

SELECTED_CORE=""
for core_path in "${CANDIDATE_CORES[@]}"; do
    if [ -f "${core_path}" ]; then
        SELECTED_CORE="${core_path}"
        break
    fi
done

if [ ! -f "${CUE_FILE}" ]; then
    echo "[!] Translated disc image not found. Building disc image first..."
    python3 "${PROJECT_DIR}/tools/rebuilder.py"
fi

if [ -n "${SELECTED_CORE}" ]; then
    echo "[*] Launching Persona with Core: ${SELECTED_CORE}"
    retroarch -L "${SELECTED_CORE}" "${CUE_FILE}"
else
    echo "[*] Launching Persona with RetroArch default configuration..."
    retroarch "${CUE_FILE}"
fi
