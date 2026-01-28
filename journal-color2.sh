#!/bin/bash
# Usage: ./journal-color-service.sh SERVICE1 SERVICE2 ...

SERVICES=("$@")
COLORS=(
	# "\033[34m" # blau normal
	# "\033[36m" # cyan
	"\033[35m" # magenta
	"\033[94m" # blau clar (light blue)
	"\033[96m" # cyan clar (light cyan)
	"\033[95m" # magenta clar (light magenta)
	"\033[38;5;27m" # blau fosc 256 colors
	"\033[38;5;33m" # blau mitjà 256 colors
	"\033[38;5;39m" # blau clar 256 colors
	"\033[38;5;63m" # cyan suau 256 colors
	"\033[38;5;99m" # magenta suau 256 colors
	"\033[38;5;123m" # cyan / blau molt clar 256 colors
	)
RESET="\033[0m"

declare -A SERVICE_COLOR
for i in "${!SERVICES[@]}"; do
	SERVICE_COLOR["${SERVICES[$i]}"]="${COLORS[$((i % ${#COLORS[@]}))]}"
done

journalctl -n 150 -f -o short $(printf -- "-u %s " "${SERVICES[@]}") | while read -r line; do
	colored=false
	for svc in "${SERVICES[@]}"; do
		# Si la línia conté "nomdelservei[" en qualsevol lloc, pintem
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
