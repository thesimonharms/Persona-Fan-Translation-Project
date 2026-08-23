#!/bin/bash
# play_persona.sh - Quick launcher for Megami Ibunroku Persona (English Fan Translation)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CUE_FILE="${PROJECT_DIR}/build/Megami_Ibunroku_Persona_EN.cue"
CORE="${HOME}/.config/retroarch/cores/swanstation_libretro.so"

if [ ! -f "${CUE_FILE}" ]; then
    echo "[!] Translated disc image not found. Building disc image first..."
    python3 "${PROJECT_DIR}/tools/rebuilder.py"
fi

if [ -f "${CORE}" ]; then
    echo "[*] Launching Persona with SwanStation (DuckStation) PSX Core..."
    retroarch -L "${CORE}" "${CUE_FILE}"
else
    echo "[*] Launching Persona with RetroArch default core..."
    retroarch "${CUE_FILE}"
fi
