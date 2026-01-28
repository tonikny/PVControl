#!/bin/bash
# Script de test para solucionar problema de read con curl | bash

echo "=== TEST DE READ CON CURL | BASH ==="
echo ""

# Método 1: Intentar con /dev/tty
echo "--- Método 1: Usando read < /dev/tty ---"
echo "Por favor, escribe algo y presiona Enter:"
if read -r entrada1 < /dev/tty; then
    echo "✓ Leído: $entrada1"
else
    echo "✗ Error con /dev/tty"
fi
echo ""

# Método 2: Verificar si stdin es terminal
echo "--- Método 2: Verificando tipo de stdin ---"
if [ -t 0 ]; then
    echo "✓ stdin es un terminal (tty)"
    ES_TTY=true
else
    echo "✗ stdin NO es un terminal (probablemente pipe)"
    ES_TTY=false
fi
echo ""

# Método 3: Intentar leer directamente
echo "--- Método 3: Read normal ---"
echo "Escribe algo: "
if read -r entrada2; then
    echo "✓ Leído: $entrada2"
else
    echo "✗ No se pudo leer (probablemente EOF)"
fi
echo ""

# Método 4: Solución alternativa - usar timeout
echo "--- Método 4: Con timeout y fallback ---"
echo "Tienes 5 segundos para escribir algo... (o se usará valor por defecto)"
entrada4="valor_por_defecto"
if read -t 5 -r respuesta4; then
    entrada4="$respuesta4"
    echo "✓ Leído: $entrada4"
else
    echo "✗ Timeout, usando valor por defecto: $entrada4"
fi
echo ""

# Método 5: Para instaladores - continuar automáticamente
echo "--- Método 5: Para instaladores (recomendado) ---"
echo "La instalación comenzará en 5 segundos..."
echo "Presiona Ctrl+C para cancelar"
for i in {5..1}; do
    echo -n "$i... "
    sleep 1
done
echo ""
echo "✓ Continuando instalación..."
echo ""

# Resumen
echo "=== RESUMEN ==="
echo "Para scripts con 'curl | bash', recomiendo:"
echo "1. NO usar 'read' para confirmaciones"
echo "2. Usar pausas con 'sleep' y permitir Ctrl+C"
echo "3. O descargar primero y ejecutar después:"
echo "   curl -sSL URL > instalador.sh"
echo "   chmod +x instalador.sh"
echo "   ./instalador.sh"
echo ""
echo "Script de test completado."