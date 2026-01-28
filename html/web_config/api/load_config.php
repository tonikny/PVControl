<?php
header('Content-Type: application/json');

$data = json_decode(file_get_contents('php://input'), true);
$file = $data['file'] ?? 'Parametros_FV_DIST_NUEVO.py';

try {
    $filePath = '/home/pi/PVControl+/' . $file;
    
    if (!file_exists($filePath)) {
        throw new Exception("Archivo no encontrado: $filePath");
    }
    
    // Leer el archivo completo
    $content = file_get_contents($filePath);
    $lines = file($filePath);
    
    // Extraer CONFIG
    $result = extractConfigWithLineNumbers($content, $lines);
    
    echo json_encode([
        'success' => true,
        'config' => $result['config'],
        'lineMap' => $result['lineMap'],
        'file' => $file,
        'fullContent' => $content
    ]);
    
} catch (Exception $e) {
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}

function extractConfigWithLineNumbers($content, $lines) {
    // Buscar CONFIG = {
    $configStartLine = -1;
    $configStartIndex = -1;
    
    for ($i = 0; $i < count($lines); $i++) {
        if (strpos($lines[$i], 'CONFIG = {') !== false) {
            $configStartLine = $i;
            $configStartIndex = strpos($content, 'CONFIG = {');
            break;
        }
    }
    
    if ($configStartLine === -1) {
        throw new Exception("No se encontró CONFIG en el archivo");
    }
    
    // Encontrar el cierre del diccionario CONFIG
    $currentPos = $configStartIndex;
    $braceCount = 0;
    $inString = false;
    $escapeNext = false;
    $stringChar = '';
    
    $contentLength = strlen($content);
    $configEndIndex = $currentPos;
    
    for ($i = $currentPos; $i < $contentLength; $i++) {
        $char = $content[$i];
        
        if ($escapeNext) {
            $escapeNext = false;
            continue;
        }
        
        if ($inString) {
            if ($char === $stringChar) {
                $inString = false;
            } elseif ($char === '\\') {
                $escapeNext = true;
            }
            continue;
        }
        
        if ($char === '"' || $char === "'") {
            $inString = true;
            $stringChar = $char;
            continue;
        }
        
        if ($char === '{') {
            $braceCount++;
        } elseif ($char === '}') {
            $braceCount--;
            if ($braceCount === 0) {
                $configEndIndex = $i;
                break;
            }
        }
    }
    
    if ($braceCount !== 0) {
        throw new Exception("CONFIG no está bien balanceado");
    }
    
    // Extraer el contenido de CONFIG (después de "CONFIG = {" hasta la llave de cierre)
    $configContent = substr($content, $configStartIndex + 10, $configEndIndex - $configStartIndex - 10);
    
    // Parsear CONFIG
    $config = parsePythonDictComplete($configContent);
    
    // Construir mapeo de líneas
    $lineMap = buildCompleteLineMap($configContent, $configStartLine + 1, $lines);
    
    return [
        'config' => $config,
        'lineMap' => $lineMap,
        'startLine' => $configStartLine,
        'endLine' => findLineNumber($content, $configEndIndex, $lines),
        'fullContent' => $content
    ];
}

function parsePythonDictComplete($content) {
    $content = trim($content);
    if (empty($content)) return [];
    
    $result = [];
    $lines = explode("\n", $content);
    $currentKey = null;
    $currentValue = '';
    $braceCount = 0;
    $bracketCount = 0;
    $parenCount = 0;
    $inString = false;
    $stringChar = '';
    
    foreach ($lines as $line) {
        $trimmedLine = trim($line);
        if (empty($trimmedLine)) continue;
        
        // Si no estamos en medio de procesar un valor, buscar nueva clave
        if ($currentKey === null && $braceCount === 0 && $bracketCount === 0 && $parenCount === 0 && !$inString) {
            if (preg_match("/^['\"]([^'\"]+)['\"]\s*:\s*(.+)$/", $trimmedLine, $matches)) {
                $currentKey = $matches[1];
                $currentValue = $matches[2];
                
                // Contar estructuras en el valor inicial
                $braceCount = countStructures($currentValue, '{', '}');
                $bracketCount = countStructures($currentValue, '[', ']');
                $parenCount = countStructures($currentValue, '(', ')');
                
                // Si no hay estructuras anidadas, procesar inmediatamente
                if ($braceCount === 0 && $bracketCount === 0 && $parenCount === 0) {
                    $result[$currentKey] = parsePythonValueComplete(trim($currentValue));
                    $currentKey = null;
                    $currentValue = '';
                }
            }
        } elseif ($currentKey !== null) {
            // Continuar acumulando el valor
            $currentValue .= "\n" . $line;
            
            // Actualizar contadores de estructuras
            $braceCount += countStructures($line, '{', '}');
            $bracketCount += countStructures($line, '[', ']');
            $parenCount += countStructures($line, '(', ')');
            
            // Si terminaron todas las estructuras, procesar el valor
            if ($braceCount === 0 && $bracketCount === 0 && $parenCount === 0) {
                $result[$currentKey] = parsePythonValueComplete(trim($currentValue));
                $currentKey = null;
                $currentValue = '';
            }
        }
        
        // Actualizar estado de string
        $inString = updateStringState($line, $inString, $stringChar);
    }
    
    // Procesar último valor si queda
    if ($currentKey !== null) {
        $result[$currentKey] = parsePythonValueComplete(trim($currentValue));
    }
    
    return $result;
}

function countStructures($text, $openChar, $closeChar) {
    $count = 0;
    $inString = false;
    $stringChar = '';
    $escapeNext = false;
    
    for ($i = 0; $i < strlen($text); $i++) {
        $char = $text[$i];
        
        if ($escapeNext) {
            $escapeNext = false;
            continue;
        }
        
        if ($inString) {
            if ($char === $stringChar) {
                $inString = false;
            } elseif ($char === '\\') {
                $escapeNext = true;
            }
            continue;
        }
        
        if ($char === '"' || $char === "'") {
            $inString = true;
            $stringChar = $char;
            continue;
        }
        
        if ($char === $openChar) {
            $count++;
        } elseif ($char === $closeChar) {
            $count--;
        }
    }
    
    return $count;
}

function updateStringState($line, $currentInString, $currentStringChar) {
    $inString = $currentInString;
    $stringChar = $currentStringChar;
    $escapeNext = false;
    
    for ($i = 0; $i < strlen($line); $i++) {
        $char = $line[$i];
        
        if ($escapeNext) {
            $escapeNext = false;
            continue;
        }
        
        if ($inString) {
            if ($char === $stringChar) {
                $inString = false;
            } elseif ($char === '\\') {
                $escapeNext = true;
            }
        } else {
            if ($char === '"' || $char === "'") {
                $inString = true;
                $stringChar = $char;
            }
        }
    }
    
    return $inString;
}

function parsePythonValueComplete($value) {
    $value = trim($value);
    
    // None
    if ($value === 'None') return null;
    
    // Booleanos
    if ($value === 'True') return true;
    if ($value === 'False') return false;
    
    // Números
    if (is_numeric($value)) {
        return strpos($value, '.') !== false ? floatval($value) : intval($value);
    }
    
    // Strings (entre comillas simples o dobles)
    if ((str_starts_with($value, "'") && str_ends_with($value, "'")) ||
        (str_starts_with($value, '"') && str_ends_with($value, '"'))) {
        return substr($value, 1, -1);
    }
    
    // Arrays - manejar arrays vacíos y con contenido
    if (str_starts_with($value, '[') && str_ends_with($value, ']')) {
        $content = trim(substr($value, 1, -1));
        if (empty($content)) return [];
        
        // Parsear elementos del array
        return parsePythonArray($content);
    }
    
    // Diccionarios
    if (str_starts_with($value, '{') && str_ends_with($value, '}')) {
        $content = trim(substr($value, 1, -1));
        if (empty($content)) return [];
        
        return parsePythonDictComplete($content);
    }
    
    // Valor por defecto (string)
    return $value;
}

function parsePythonArray($content) {
    $content = trim($content);
    if (empty($content)) return [];
    
    $items = [];
    $currentItem = '';
    $braceCount = 0;
    $bracketCount = 0;
    $parenCount = 0;
    $inString = false;
    $stringChar = '';
    
    for ($i = 0; $i < strlen($content); $i++) {
        $char = $content[$i];
        
        if ($inString) {
            $currentItem .= $char;
            if ($char === $stringChar) {
                $inString = false;
            }
            continue;
        }
        
        if ($char === '"' || $char === "'") {
            $inString = true;
            $stringChar = $char;
            $currentItem .= $char;
            continue;
        }
        
        if ($char === '{') $braceCount++;
        if ($char === '}') $braceCount--;
        if ($char === '[') $bracketCount++;
        if ($char === ']') $bracketCount--;
        if ($char === '(') $parenCount++;
        if ($char === ')') $parenCount--;
        
        if ($char === ',' && $braceCount === 0 && $bracketCount === 0 && $parenCount === 0) {
            // Fin de un item
            $items[] = parsePythonValueComplete(trim($currentItem));
            $currentItem = '';
        } else {
            $currentItem .= $char;
        }
    }
    
    // Agregar el último item
    if (!empty(trim($currentItem))) {
        $items[] = parsePythonValueComplete(trim($currentItem));
    }
    
    return $items;
}

function buildCompleteLineMap($configContent, $startLine, $allLines) {
    $lineMap = [];
    $lines = explode("\n", $configContent);
    
    for ($i = 0; $i < count($lines); $i++) {
        $line = $lines[$i];
        $trimmed = trim($line);
        
        if (empty($trimmed)) continue;
        
        // Buscar patrones de clave
        if (preg_match("/^['\"]([^'\"]+)['\"]\s*:/", $trimmed, $matches)) {
            $key = $matches[1];
            $currentLine = $startLine + $i;
            
            // Extraer el contenido EXACTO (RAW) de esta sección
            $sectionContent = extractRawSectionContent($lines, $i);
            
            // Construir el path completo
            $path = 'CONFIG.' . $key;
            
            // Guardar en lineMap
            $lineMap[$path] = [
                'startLine' => $currentLine,
                'content' => $sectionContent
            ];
        }
    }
    
    return $lineMap;
}

function extractRawSectionContent($lines, $startIndex) {
    $content = '';
    $inSection = false;
    $baseIndent = 0;
    
    for ($i = $startIndex; $i < count($lines); $i++) {
        $line = $lines[$i];
        $trimmed = trim($line);
        
        if (!$inSection) {
            // En la línea inicial, tomar toda la línea
            $content = $line;
            $inSection = true;
            
            // Calcular la indentación base
            $baseIndent = strlen($line) - strlen(ltrim($line));
            continue;
        }
        
        // Calcular indentación actual
        $currentIndent = strlen($line) - strlen(ltrim($line));
        
        // Si la indentación es menor o igual a la base Y no es la línea inicial
        // Y es una nueva clave o cierre, terminar
        if ($currentIndent <= $baseIndent && $i > $startIndex) {
            if (preg_match("/^['\"]([^'\"]+)['\"]\s*:/", $trimmed) || $trimmed === '}' || $trimmed === '},') {
                break;
            }
        }
        
        // Agregar la línea al contenido
        $content .= "\n" . $line;
        
        // Si encontramos el cierre de CONFIG, terminar
        if ($trimmed === '}') {
            break;
        }
    }
    
    return $content;
}

function extractCompleteSectionContent($lines, $startIndex) {
    $content = '';
    $totalBraceCount = 0;
    $totalBracketCount = 0;
    $totalParenCount = 0;
    $inSection = false;
    
    for ($i = $startIndex; $i < count($lines); $i++) {
        $line = $lines[$i];
        $trimmedLine = trim($line);
        
        if (!$inSection) {
            // En la línea inicial, tomar todo después del :
            $colonPos = strpos($line, ':');
            if ($colonPos !== false) {
                $content = substr($line, $colonPos + 1);
                $inSection = true;
                
                // Contar estructuras iniciales
                $totalBraceCount = countStructures($content, '{', '}');
                $totalBracketCount = countStructures($content, '[', ']');
                $totalParenCount = countStructures($content, '(', ')');
            }
        } else {
            // Solo agregar la línea si no hemos terminado la sección
            $content .= "\n" . $line;
            
            // Actualizar contadores totales
            $totalBraceCount += countStructures($line, '{', '}');
            $totalBracketCount += countStructures($line, '[', ']');
            $totalParenCount += countStructures($line, '(', ')');
            
            // DEBUG: Mostrar contadores
            // error_log("Línea $i: braces=$totalBraceCount, brackets=$totalBracketCount, parens=$totalParenCount");
            
            // Verificar si debemos terminar
            if ($totalBraceCount === 0 && $totalBracketCount === 0 && $totalParenCount === 0) {
                // Solo terminar si estamos seguros de que es el final de esta sección
                $nextLineIndex = $i + 1;
                if ($nextLineIndex < count($lines)) {
                    $nextLine = $lines[$nextLineIndex];
                    $nextTrimmed = trim($nextLine);
                    
                    // Si la siguiente línea es una nueva clave al mismo nivel, terminar
                    if (preg_match("/^['\"]([^'\"]+)['\"]\s*:/", $nextTrimmed)) {
                        break;
                    }
                    
                    // Si la siguiente línea es el cierre del nivel padre, terminar
                    if ($nextTrimmed === '}' || $nextTrimmed === '},') {
                        break;
                    }
                    
                    // Si la siguiente línea está vacía y estamos en nivel 0, podría ser el final
                    if (empty($nextTrimmed) && $i > $startIndex + 2) {
                        break;
                    }
                } else {
                    // Última línea del archivo
                    break;
                }
            }
        }
    }
    
    $result = trim($content);
    
    // Limpiar comas finales que puedan quedar
    while (str_ends_with($result, ',')) {
        $result = substr($result, 0, -1);
    }
    
    return $result;
}


function findLineNumber($content, $pos, $lines) {
    $currentPos = 0;
    for ($i = 0; $i < count($lines); $i++) {
        $lineLength = strlen($lines[$i]);
        if ($currentPos + $lineLength > $pos) {
            return $i;
        }
        $currentPos += $lineLength;
    }
    return count($lines) - 1;
}

// Funciones de compatibilidad
if (!function_exists('str_starts_with')) {
    function str_starts_with($haystack, $needle) {
        return strpos($haystack, $needle) === 0;
    }
}

if (!function_exists('str_ends_with')) {
    function str_ends_with($haystack, $needle) {
        return substr($haystack, -strlen($needle)) === $needle;
    }
}
?>