#!/bin/bash
# Usage:
#   ./journal-color.sh [journalctl options]
#   ./journal-color.sh -u service1 -u service2 -f

COLORS=(
  "\033[35m"
  "\033[94m"
  "\033[96m"
  "\033[95m"
  "\033[38;5;27m"
  "\033[38;5;33m"
  "\033[38;5;39m"
  "\033[38;5;63m"
  "\033[38;5;99m"
  "\033[38;5;123m"
)
RESET="\033[0m"

# ─────────────────────────────────────────────
# 1️⃣ Extreure serveis passats amb -u
# ─────────────────────────────────────────────
SERVICES=()
ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -u|--unit)
      SERVICES+=("$2")
      ARGS+=("$1" "$2")
      shift 2
      ;;
    *)
      ARGS+=("$1")
      shift
      ;;
  esac
done

# ─────────────────────────────────────────────
# 2️⃣ Assignar colors només si hi ha serveis
# ─────────────────────────────────────────────
declare -A SERVICE_COLOR
for i in "${!SERVICES[@]}"; do
  SERVICE_COLOR["${SERVICES[$i]}"]="${COLORS[$((i % ${#COLORS[@]}))]}"
done

# ─────────────────────────────────────────────
# 3️⃣ Executar journalctl amb TOTS els arguments
# ─────────────────────────────────────────────
journalctl -o short "${ARGS[@]}" | while read -r line; do
  if ((${#SERVICES[@]} == 0)); then
    # Cap -u → comportament normal
    echo "$line"
    continue
  fi

  colored=false
  for svc in "${SERVICES[@]}"; do
    if [[ "$line" == *"$svc["* ]]; then
      echo -e "${SERVICE_COLOR[$svc]}${line}${RESET}"
      colored=true
      break
    fi
  done

  if [ "$colored" = false ]; then
    echo "$line"
  fi
done
