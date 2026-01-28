import configManager from './configManager.js';

const activeModals = {}; // Objeto para mantener el seguimiento de las ventanas emergentes activas
let currentLineState = {}; // Mantener el estado actual de las líneas para determinar si se necesita redibujar

window.toggleMenu = toggleMenu;

document.addEventListener('DOMContentLoaded', async function () {
  const button = document.createElement('button');
  button.textContent = 'Cambiar Configuración';
  button.onclick = () => {
    nuevaConfiguracion();
  };
  document.body.appendChild(button);

  const file = await fetchActiveConfig();
  await configManager.loadConfig(file);
  initializeApp();
});

async function fetchActiveConfig() {
  const response = await fetch('configuracion_activa.txt');
  const file = await response.text();
  return file.trim();
}

function initializeApp() {
  // reinicializo aplicación con la nueva configuración
  console.log('Aplicación inicializada con la nueva configuración');
  // Llama a tus funciones de inicialización aquí
  const config = configManager.getConfig();
  init();
  generateMenu(config.menu_web);

  const blockMargin = config.blockMargin || '20px 20px';
  const styleSheet = document.getElementById('dynamicStyles').sheet;

  styleSheet.insertRule(
    `.block { margin: ${blockMargin}; }`,
    styleSheet.cssRules.length
  );
}

function nuevaConfiguracion() {
  fetch('configuraciones/')
    .then((response) => response.text())
    .then((data) => {
      const parser = new DOMParser();
      const doc = parser.parseFromString(data, 'text/html');
      const links = doc.querySelectorAll('a');
      const configFiles = Array.from(links)
        .map((link) => link.getAttribute('href'))
        .filter((file) => file.endsWith('.json'));

      displayConfigOptions(configFiles);
    });
}

function displayConfigOptions(configFiles) {
  const container = document.createElement('div');
  configFiles.forEach((file) => {
    const button = document.createElement('button');
    button.textContent = file;
    button.onclick = async () => {
      updateActiveConfigFile(file);
      await configManager.loadConfig(file);
      initializeApp();
    };
    container.appendChild(button);
  });
  document.body.appendChild(container);
}

function updateActiveConfigFile(file) {
  console.log('Intentando grabar archivo', file);

  fetch('configuracion_actualizacion.php', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ file }),
  }).then((response) => {
    if (response.ok) {
      console.log('Archivo de configuración actualizado: ', file);
    } else {
      console.error('Error al actualizar el archivo de configuración');
    }
  });
}

// Función para hacer una ventana modal arrastrable
function makeDraggable(element) {
  var pos1 = 0,
    pos2 = 0,
    pos3 = 0,
    pos4 = 0;
  var header = element.querySelector('.modal-header');
  if (header) {
    header.onmousedown = dragMouseDown;
    header.ontouchstart = dragTouchStart;
  } else {
    element.onmousedown = dragMouseDown;
    element.ontouchstart = dragTouchStart;
  }

  function dragMouseDown(e) {
    e.preventDefault();
    pos3 = e.clientX;
    pos4 = e.clientY;
    document.onmouseup = closeDragElement;
    document.onmousemove = elementDrag;
  }

  function dragTouchStart(e) {
    e.preventDefault();
    pos3 = e.touches[0].clientX;
    pos4 = e.touches[0].clientY;
    document.ontouchend = closeDragElement;
    document.ontouchmove = elementTouchDrag;
  }

  function elementDrag(e) {
    e.preventDefault();
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;
    element.style.top = element.offsetTop - pos2 + 'px';
    element.style.left = element.offsetLeft - pos1 + 'px';
  }

  function elementTouchDrag(e) {
    e.preventDefault();
    pos1 = pos3 - e.touches[0].clientX;
    pos2 = pos4 - e.touches[0].clientY;
    pos3 = e.touches[0].clientX;
    pos4 = e.touches[0].clientY;
    element.style.top = element.offsetTop - pos2 + 'px';
    element.style.left = element.offsetLeft - pos1 + 'px';
  }

  function closeDragElement() {
    document.onmouseup = null;
    document.onmousemove = null;
    document.ontouchend = null;
    document.ontouchmove = null;
  }
}

// Función para generar el menú
function generateMenu(menuConfig) {
  const menutitle = document.getElementById('menutitle');
  if (menutitle) {
    while (menutitle.firstChild) {
      menutitle.removeChild(menutitle.firstChild);
    }
  }
  Object.keys(menuConfig).forEach((menuItem) => {
    if (typeof menuConfig[menuItem] === 'string') {
      const link = document.createElement('a');
      link.href = `../${menuConfig[menuItem]}`;
      link.textContent = menuItem;
      menutitle.appendChild(link);
    } else {
      const dropdown = document.createElement('div');
      dropdown.className = 'dropdown';
      const dropbtn = document.createElement('button');
      dropbtn.className = 'dropbtn';
      dropbtn.textContent = menuItem;
      dropdown.appendChild(dropbtn);
      const dropdownContent = document.createElement('div');
      dropdownContent.className = 'dropdown-content';
      Object.keys(menuConfig[menuItem]).forEach((subMenuItem) => {
        const subLink = document.createElement('a');
        subLink.href = `../${menuConfig[menuItem][subMenuItem]}`;
        subLink.textContent = subMenuItem;
        dropdownContent.appendChild(subLink);
      });
      dropdown.appendChild(dropdownContent);
      menutitle.appendChild(dropdown);
    }
  });
}

// Función para alternar el menú en móviles
function toggleMenu() {
  const navbar = document.getElementById('navbar');
  if (navbar.className === 'navbar') {
    navbar.className += ' responsive';
  } else {
    navbar.className = 'navbar';
  }
}

function createElement(elementConfig, blockId, elementId) {
  if (
    elementConfig.visualizacion === 'nunca' ||
    elementConfig.visualizacion === 'modal'
  )
    return;

  const elementDiv = document.createElement('div');
  elementDiv.className = 'element';
  elementDiv.id = `${blockId}-${elementId}`;

  // Verificar y asignar valores por defecto
  if (!elementConfig.position) elementConfig.position = { x: 0, y: 0 };
  if (elementConfig.bold) {
    elementDiv.style.fontWeight = 'bold';
  }
  if (!elementConfig.value) {
    elementConfig.value = 0;
  }
  if (!elementConfig.unit) {
    elementConfig.unit = '';
  }

  elementDiv.style.position = 'absolute';
  elementDiv.style.left = `${elementConfig.position.x}px`;
  elementDiv.style.top = `${elementConfig.position.y}px`;
  elementDiv.style.width = `${elementConfig.width}px`;
  elementDiv.style.backgroundColor = elementConfig.backgroundColor;
  elementDiv.style.color = elementConfig.valueColor;
  elementDiv.style.fontSize = elementConfig.size;

  // Verificar el atributo showTitle y mostrar el título si corresponde
  if (elementConfig.showTitle !== false) {
    const title = document.createElement('div');
    title.innerText = elementId + ': ';
    title.style.color = elementConfig.titleColor;
    elementDiv.appendChild(title);
  }

  const value = document.createElement('div');
  value.className = 'value';

  // Verificar si el valor es un número y formatearlo con separador de miles ,comas y maximo 3 decimales
  let displayValue = elementConfig.value;
  if (typeof displayValue === 'number') {
    displayValue = displayValue.toLocaleString('de-DE', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 3,
    });
  }

  value.innerText = displayValue + ' ' + elementConfig.unit;
  value.style.color = elementConfig.valueColor;
  elementDiv.appendChild(value);

  const blockDiv = document.getElementById(blockId);
  blockDiv.appendChild(elementDiv);
}

function createBlock(blockConfig, blockId, rowDiv) {
  const blockDiv = document.createElement('div');
  blockDiv.id = blockId;
  blockDiv.className = 'block';

  if (!blockConfig.size) blockConfig.size = { width: 0, height: 0 };

  blockDiv.style.width = `${blockConfig.size.width}px`;
  blockDiv.style.height = `${blockConfig.size.height}px`;
  blockDiv.style.position = 'relative';
  blockDiv.style.backgroundColor = 'transparent'; // Fondo transparente por defecto

  // Crear una capa para la imagen
  const imgDiv = document.createElement('div');

  imgDiv.className = 'block-image'; // Añadir clase para referencia
  imgDiv.style.backgroundImage = `url(/img/equipos/${blockConfig.image})`;
  imgDiv.style.backgroundSize = 'cover';
  imgDiv.style.position = 'absolute';
  imgDiv.style.top = '5%';
  imgDiv.style.left = '5%';
  imgDiv.style.width = '90%';
  imgDiv.style.height = '90%';
  imgDiv.style.opacity = '0.99'; // Ajustar opacidad para ver el fondo
  imgDiv.style.pointerEvents = 'none'; // Para que los eventos de clic pasen a través de la imagen

  blockDiv.appendChild(imgDiv);

  // Crear imagen de advertencia oculta inicialmente
  const warningImg = document.createElement('img');
  warningImg.src = '/img/equipos/aviso.png'; // Ruta de la imagen de advertencia
  warningImg.className = 'warning-icon blink';
  warningImg.style.display = 'none'; // Oculto por defecto

  warningImg.style.position = 'absolute';
  warningImg.style.top = '0px';
  warningImg.style.right = '0px';
  warningImg.style.width = '40px';
  warningImg.style.height = '40px';

  blockDiv.appendChild(warningImg);

  blockDiv.addEventListener('click', () => showModal(blockConfig, blockId));

  rowDiv.appendChild(blockDiv);

  try {
    // Si no existen elementos saltar este bloque
    if (!blockConfig.elements) return;

    Object.keys(blockConfig.elements).forEach((elementId) => {
      createElement(blockConfig.elements[elementId], blockId, elementId);
    });
  } catch (error) {
    console.error('No existe elements en la definicion del bloque ', blockId);
    console.error('  -> Error creacion Elementos ', error);
  }
}

function createAndPositionLines() {
  const config = configManager.getConfig();
  const svg = document.getElementById('svgLines');
  // Crear un mapa de líneas actuales
  const existingLines = new Map();
  svg.querySelectorAll('line').forEach((line) => {
    const id = line.getAttribute('id');
    existingLines.set(id, line);
  });

  Object.keys(config.filas).forEach((rowId) => {
    const rowConfig = config.filas[rowId];
    Object.keys(rowConfig).forEach((blockId) => {
      const blockConfig = rowConfig[blockId];

      if (!blockConfig.connectTo) {
        // Si no existe connectTo, saltar este bloque
        return;
      }

      // Función para procesar cada conexión
      const processConnection = (connection) => {
        try {
          // Verificar y asignar valores por defecto
          if (!connection.from) connection.from = 'bottom';
          if (!connection.to) connection.to = 'top';
          if (!connection.colorLineaPositiva)
            connection.colorLineaPositiva = 'black';
          if (!connection.colorLineaNegativa)
            connection.colorLineaNegativa = 'red';
          if (!connection.flujoLinea) connection.flujoLinea = 'normal';

          const fromBlock = document.getElementById(blockId);
          const toBlock = document.getElementById(connection.id);

          if (fromBlock && toBlock) {
            let fromX, fromY, toX, toY;
            if (connection.flujoLinea === 'normal') {
              ({ x: fromX, y: fromY } = calculateConnectionCoords(
                fromBlock,
                connection.from
              ));
              ({ x: toX, y: toY } = calculateConnectionCoords(
                toBlock,
                connection.to
              ));
            } else if (connection.flujoLinea === 'inverso') {
              ({ x: fromX, y: fromY } = calculateConnectionCoords(
                toBlock,
                connection.to
              ));
              ({ x: toX, y: toY } = calculateConnectionCoords(
                fromBlock,
                connection.from
              ));
            }

            try {
              const lineKey = `${blockId}-${connection.id}`;
              const valor = blockConfig.elements[connection.control].value;
              const controlValue = Math.abs(valor);

              const newCoords = { fromX, fromY, toX, toY };
              const strokeWidth = Math.max(
                2,
                Math.min(
                  15,
                  ((controlValue - connection.min) /
                    (connection.max - connection.min)) *
                    13 +
                    2
                )
              );

              // Verificar si las coordenadas o el valor de control han cambiado
              const currentState = currentLineState[lineKey] || {};
              if (
                !currentState.coords ||
                !currentState.controlValue ||
                currentState.coords.fromX !== fromX ||
                currentState.coords.fromY !== fromY ||
                currentState.coords.toX !== toX ||
                currentState.coords.toY !== toY ||
                currentState.valor !== valor
              ) {
                //currentState.controlValue !== controlValue) {

                //currentLineState[lineKey] = { coords: newCoords, controlValue };
                currentLineState[lineKey] = { coords: newCoords, valor };

                let line = existingLines.get(lineKey);
                if (!line) {
                  line = document.createElementNS(
                    'http://www.w3.org/2000/svg',
                    'line'
                  );
                  line.setAttribute('id', lineKey);
                  svg.appendChild(line);
                }

                line.setAttribute('x1', fromX);
                line.setAttribute('y1', fromY);
                line.setAttribute('x2', toX);
                line.setAttribute('y2', toY);
                line.setAttribute('stroke-width', strokeWidth);

                // Check if value is 0 and apply the appropriate class
                if (valor === 0) {
                  line.setAttribute('class', 'line_inactive');
                  line.removeAttribute('style');
                } else {
                  const color =
                    valor >= 0
                      ? connection.colorLineaPositiva
                      : connection.colorLineaNegativa;
                  const animation = valor >= 0 ? 'dash_normal' : 'dash_inverso';
                  line.setAttribute('class', 'line');
                  line.setAttribute(
                    'style',
                    `stroke: ${color}; animation-name: ${animation};`
                  );
                }
              }

              // Eliminar de existingLines ya procesados
              existingLines.delete(lineKey);
            } catch (error) {
              console.error('Conexion ', blockId, connection.id);
              console.error(
                'Variable control:',
                connection.control,
                ' =',
                blockConfig.elements[connection.control]
              );
              console.error(
                'Comprueba que los bloques existen y la variable de control esta bien definida'
              );
              console.error('  -> Error creacion Linea ', error);
            }
          }
        } catch (error) {
          console.error(
            'Conexion ',
            blockId,
            'Revisar parametros creacion linea a',
            connection
          );
          console.error('  -> Error creacion Linea ', error);
        }
      };

      // Detectar si connectTo es un solo objeto (antiguo formato) o un objeto con múltiples conexiones (nuevo formato)
      if (blockConfig.connectTo.id) {
        // Formato antiguo (única línea)
        processConnection(blockConfig.connectTo, 'single');
      } else {
        // Formato nuevo (múltiples líneas)
        Object.keys(blockConfig.connectTo).forEach((key) => {
          processConnection(blockConfig.connectTo[key], key);
        });
      }
    });
  });

  // Remover las líneas que ya no son necesarias
  existingLines.forEach((line) => {
    svg.removeChild(line);
  });
}

function calculateConnectionCoords(block, position) {
  const rect = block.getBoundingClientRect();
  const svgRect = document.getElementById('svgLines').getBoundingClientRect();

  let x, y;

  switch (position) {
    case 'top':
      x = rect.left + rect.width / 2 - svgRect.left;
      y = rect.top - svgRect.top;
      break;
    case 'bottom':
      x = rect.left + rect.width / 2 - svgRect.left;
      y = rect.bottom - svgRect.top;
      break;
    case 'left':
      x = rect.left - svgRect.left;
      y = rect.top + rect.height / 2 - svgRect.top;
      break;
    case 'right':
      x = rect.right - svgRect.left;
      y = rect.top + rect.height / 2 - svgRect.top;
      break;
    default:
      x = rect.left + rect.width / 2 - svgRect.left;
      y = rect.top + rect.height / 2 - svgRect.top;
      break;
  }

  return { x, y };
}

function init() {
  const config = configManager.getConfig();
  const central = document.getElementById('central');

  // Borrar filas antiguas
  while (central.lastChild?.id?.includes('fila')) {
    central.removeChild(central.lastChild);
  }
  // Crear filas
  Object.keys(config.filas).forEach((rowId) => {
    const rowConfig = config.filas[rowId];
    const rowDiv = document.createElement('div');
    rowDiv.id = rowId;
    rowDiv.className = 'row';
    central.appendChild(rowDiv);
    Object.keys(rowConfig).forEach((blockId) => {
      createBlock(rowConfig[blockId], blockId, rowDiv);
    });
  });

  // Crear laterales
  if (config.laterales.izquierdo) {
    const bloqueIzquierdo = document.getElementById('izquierdo');
    while (bloqueIzquierdo.firstChild) {
      bloqueIzquierdo.removeChild(bloqueIzquierdo.firstChild);
    }
    Object.keys(config.laterales.izquierdo.elements).forEach((elementId) => {
      createSideBlockElement(
        bloqueIzquierdo,
        config.laterales.izquierdo.elements[elementId],
        elementId,
        'izquierdo'
      );
    });
  }
  if (config.laterales.derecho) {
    const bloqueDerecho = document.getElementById('derecho');
    Object.keys(config.laterales.derecho.elements).forEach((elementId) => {
      createSideBlockElement(
        bloqueDerecho,
        config.laterales.derecho.elements[elementId],
        elementId,
        'derecho'
      );
    });
  }

  fetchAndUpdateData();

  setInterval(fetchAndUpdateData, 10000);
}

async function fetchAndUpdateData() {
  let data = '';
  try {
    const response = await fetch('d_fv.php');
    data = await response.json();
    updateValues(data);
    createAndPositionLines();
  } catch (error) {
    console.error('Error actualizacion datos:', error);
  }
}

function updateValues1(data) {
  const d_ = Object.assign({}, data);

  const config = configManager.getConfig();

  const now = new Date(); // Hora actual
  console.log(now, 'data', data);
  //console.log('d_', d_);

  Object.keys(config.filas).forEach((rowId) => {
    const rowConfig = config.filas[rowId];
    Object.keys(rowConfig).forEach((blockId) => {
      const blockConfig = rowConfig[blockId];

      //console.log('BLOQUE: ', blockId );

      // Verificar avisos bloque y actualizar fondo y logo
      let avisoActivado = false;
      if (blockConfig.avisos) {
        const blockDiv = document.getElementById(blockId);
        let warningImg = blockDiv.querySelector('.warning-icon');
        Object.keys(blockConfig.avisos).forEach((key) => {
          const aviso = blockConfig.avisos[key];
          const condicion = new Function(
            'd_',
            'now',
            `return ${aviso.condicion};`
          );

          try {
            if (condicion(d_, now)) {
              blockDiv.style.backgroundColor = aviso.color;

              avisoActivado = true;

              if (!warningImg) {
                console.log('creando imagen aviso'); //no deberia ejecutarse nunca
                warningImg = document.createElement('img');
                warningImg.src = 'aviso.png';
                warningImg.className = 'warning-icon blink'; // Agregar la clase blink
                blockDiv.appendChild(warningImg);
              }
              warningImg.style.display = 'block'; // Corregir a style.display
              //return true; // Salir del bucle si se cumple una condición
            }
          } catch {
            console.error(
              'Error en condicion del Bloque:',
              blockId,
              ' ->',
              aviso.condicion
            );
          }

          //return false; // Continuar si no se cumple la condición
        });

        if (!avisoActivado && warningImg) {
          warningImg.style.display = 'none';
          blockDiv.style.backgroundColor = 'transparent'; // Restaurar el fondo a transparente
        }
      }

      try {
        // Si no existen elementos saltar este bloque
        if (!blockConfig.elements) return;

        Object.keys(blockConfig.elements).forEach((elementId) => {
          const elementConfig = blockConfig.elements[elementId];

          //console.log('    - Elem.', elementId );

          try {
            let value = null;
            if (elementConfig.sensor) value = eval(elementConfig.sensor);
            else if (elementConfig.campoBD)
              value = getValueFromData(data, elementConfig.campoBD);

            //console.log(' ->',elementId,': ', value );

            if (value !== null) {
              let value_adap = value;

              elementConfig.value = value;
              const elementDiv = document.getElementById(
                `${blockId}-${elementId}`
              );
              // Comprobar avisos a nivel elemento
              if (elementConfig.avisos) {
                Object.keys(elementConfig.avisos).forEach((key) => {
                  const aviso = elementConfig.avisos[key];
                  const condicion = new Function(
                    'value',
                    'd_',
                    'now',
                    `return ${aviso.condicion};`
                  );
                  if (condicion(value, data, now)) {
                    if (aviso.color)
                      elementDiv.style.backgroundColor = aviso.color; //por compatibilidad
                    if (aviso.backgroundColor)
                      elementDiv.style.backgroundColor = aviso.backgroundColor;
                    if (aviso.position) {
                      elementDiv.style.left = `${aviso.position.x}px`;
                      elementDiv.style.top = `${aviso.position.y}px`;
                    }
                    if (aviso.size) elementDiv.style.fontSize = aviso.size;
                    if (aviso.bold) elementDiv.style.fontWeight = aviso.bold;
                    if (aviso.width)
                      elementDiv.style.width = `${aviso.width}px`;
                    if (aviso.valueColor) {
                      //Color texto
                      const valueDiv = elementDiv.querySelector('.value');
                      if (valueDiv) valueDiv.style.color = aviso.valueColor; // Cambiar el color del valor

                      //return true;
                    }

                    //return true;
                  }
                  //return false; // Continuar si no se cumple la condición
                });
              }

              if (elementDiv) {
                const valueDiv = elementDiv.querySelector('.value');
                if (valueDiv) {
                  if (typeof value === 'number') {
                    value_adap = value.toLocaleString('de-DE', {
                      minimumFractionDigits: 0,
                      maximumFractionDigits: 3,
                    });
                  }
                  valueDiv.innerHTML = value_adap + ' ' + elementConfig.unit;
                }
              }
            }
          } catch {
            console.error(
              `Error al evaluar sensor ${elementConfig.sensor} en el elemento ${elementId}:`
            );
          }
        });
      } catch (error) {
        console.error(
          'Error actualizacion elementos en bloque :',
          blockId,
          error
        );
      }
    });
  });

  // Actualizar las ventanas modales activas
  updateModalValues(data);

  function updateSideBlock(sideBlock, side) {
    Object.keys(sideBlock.elements).forEach((elementId) => {
      const elementConfig = sideBlock.elements[elementId];

      if (!elementConfig.campoBD) elementConfig.campoBD = '';

      let value = null;
      if (elementConfig.campoBD != '') {
        value = getValueFromData(data, elementConfig.campoBD);
      } else {
        value = elementConfig.value;
      }

      if (value !== null) {
        elementConfig.value = value;
        const elementDiv = document.getElementById(`${side}-${elementId}`);
        if (elementDiv) {
          const valueDiv = elementDiv.querySelector('.value');
          if (valueDiv) {
            valueDiv.innerHTML = value + ' ' + elementConfig.unit;
          }

          // comprobar condiciones en sideBlock
          if (elementConfig.avisos) {
            //console.log('Aviso.side',elementConfig.avisos);
            Object.keys(elementConfig.avisos).forEach((key) => {
              const aviso = elementConfig.avisos[key];

              const condicion = new Function(
                'value',
                'data',
                'now',
                `return ${aviso.condicion};`
              );

              //console.log(key,' -Evaluando condicion', aviso.condicion);
              if (condicion(value, data, now)) {
                if (aviso.color) elementDiv.style.backgroundColor = aviso.color; //por compatibilidad
                if (aviso.backgroundColor)
                  elementDiv.style.backgroundColor = aviso.backgroundColor;
                if (aviso.size) elementDiv.style.fontSize = aviso.size;
                if (aviso.bold) elementDiv.style.fontWeight = aviso.bold;
                if (aviso.width) elementDiv.style.width = `${aviso.width}px`;
                if (aviso.valueColor) {
                  //Color texto
                  const valueDiv = elementDiv.querySelector('.value');
                  if (valueDiv) valueDiv.style.color = aviso.valueColor; // Cambiar el color del valor
                }
              }
            });
          }
        }
      }
    });
  }

  if (config.laterales.izquierdo) {
    updateSideBlock(config.laterales.izquierdo, 'izquierdo');
  }

  if (config.laterales.derecho) {
    updateSideBlock(config.laterales.derecho, 'derecho');
  }
}

function updateValues(data) {
  const d_ = Object.assign({}, data);

  const config = configManager.getConfig();
  const now = new Date(); // Hora actual
  //console.log(now, 'data', data);
  //console.log('d_', d_);

  Object.keys(config.filas).forEach((rowId) => {
    const rowConfig = config.filas[rowId];
    Object.keys(rowConfig).forEach((blockId) => {
      const blockConfig = rowConfig[blockId];

      //console.log('BLOQUE: ', blockId );

      // Verificar avisos bloque y actualizar fondo, logo y imagen
      let avisoActivado = false;
      if (blockConfig.avisos) {
        const blockDiv = document.getElementById(blockId);
        let warningImg = blockDiv.querySelector('.warning-icon');
        let blockImgDiv = blockDiv.querySelector('.block-image');

        //console.log(blockId, blockImgDiv);

        Object.keys(blockConfig.avisos).forEach((key) => {
          const aviso = blockConfig.avisos[key];
          const condicion = new Function(
            'd_',
            'now',
            `return ${aviso.condicion};`
          );

          try {
            if (condicion(d_, now)) {
              if (aviso.color) blockDiv.style.backgroundColor = aviso.color;
              if (aviso.image)
                blockImgDiv.style.backgroundImage = `url(/img/equipos/${aviso.image})`;
              if (aviso.size) {
                blockDiv.style.width = `${aviso.size.width}px`;
                blockDiv.style.height = `${aviso.size.height}px`;
              }
              if (aviso.verAviso !== false) {
                avisoActivado = true;
                if (!warningImg) {
                  warningImg = document.createElement('img');
                  warningImg.src = 'aviso.png';
                  warningImg.className = 'warning-icon blink'; // Agregar la clase blink
                  blockDiv.appendChild(warningImg);
                }
                warningImg.style.display = 'block'; // Corregir a style.display
              } else {
                warningImg.style.display = 'none';
              }
            }
          } catch {
            console.error(
              'Error en condicion del Bloque:',
              blockId,
              ' ->',
              aviso.condicion
            );
          }
        });

        if (!avisoActivado && warningImg) {
          warningImg.style.display = 'none';
          blockDiv.style.backgroundColor = 'transparent'; // Restaurar el fondo a transparente
        }
      }

      try {
        // Si no existen elementos saltar este bloque
        if (!blockConfig.elements) return;

        Object.keys(blockConfig.elements).forEach((elementId) => {
          const elementConfig = blockConfig.elements[elementId];

          //console.log('    - Elem.', elementId );

          try {
            let value = null;
            if (elementConfig.sensor) value = eval(elementConfig.sensor);
            else if (elementConfig.campoBD)
              value = getValueFromData(data, elementConfig.campoBD);

            //console.log(' ->',elementId,': ', value );

            if (value !== null) {
              let value_adap = value;

              elementConfig.value = value;
              const elementDiv = document.getElementById(
                `${blockId}-${elementId}`
              );
              // Comprobar avisos a nivel elemento
              let existeAviso = false;

              if (elementConfig.avisos) {
                Object.keys(elementConfig.avisos).forEach((key) => {
                  const aviso = elementConfig.avisos[key];
                  const condicion = new Function(
                    'value',
                    'd_',
                    'now',
                    `return ${aviso.condicion};`
                  );
                  if (condicion(value, data, now)) {
                    existeAviso = true;

                    if (aviso.color)
                      elementDiv.style.backgroundColor = aviso.color; //por compatibilidad
                    if (aviso.backgroundColor)
                      elementDiv.style.backgroundColor = aviso.backgroundColor;
                    if (aviso.position) {
                      elementDiv.style.left = `${aviso.position.x}px`;
                      elementDiv.style.top = `${aviso.position.y}px`;
                    }
                    if (aviso.size) elementDiv.style.fontSize = aviso.size;
                    if (aviso.bold) elementDiv.style.fontWeight = aviso.bold;
                    if (aviso.width)
                      elementDiv.style.width = `${aviso.width}px`;
                    if (aviso.valueColor) {
                      //Color texto
                      const valueDiv = elementDiv.querySelector('.value');
                      if (valueDiv) valueDiv.style.color = aviso.valueColor; // Cambiar el color del valor

                      //return true;
                    }

                    //return true;
                  }
                  //return false; // Continuar si no se cumple la condición
                });

                if (!existeAviso) {
                  console.log(
                    blockId,
                    elementId,
                    'div_bc',
                    elementDiv.style.backgroundColor,
                    'conf_bc',
                    elementConfig.backgroundColor
                  );

                  elementDiv.style.backgroundColor =
                    elementConfig.backgroundColor;
                  elementDiv.style.left = `${elementConfig.position.x}px`;
                  elementDiv.style.top = `${elementConfig.position.y}px`;
                  const valueDiv = elementDiv.querySelector('.value');
                  valueDiv.style.color = elementConfig.valueColor;
                }
              }

              if (elementDiv) {
                const valueDiv = elementDiv.querySelector('.value');
                if (valueDiv) {
                  if (typeof value === 'number') {
                    value_adap = value.toLocaleString('de-DE', {
                      minimumFractionDigits: 0,
                      maximumFractionDigits: 3,
                    });
                  }
                  valueDiv.innerHTML = value_adap + ' ' + elementConfig.unit;
                }
              }
            }
          } catch {
            console.error(
              `Error al evaluar sensor ${elementConfig.sensor} en el elemento ${elementId}:`
            );
          }
        });
      } catch (error) {
        console.error(
          'Error actualizacion elementos en bloque :',
          blockId,
          error
        );
      }
    });
  });

  // Actualizar las ventanas modales activas
  updateModalValues(data);

  function updateSideBlock(sideBlock, side) {
    Object.keys(sideBlock.elements).forEach((elementId) => {
      const elementConfig = sideBlock.elements[elementId];

      if (!elementConfig.campoBD) elementConfig.campoBD = '';

      let value = null;
      if (elementConfig.campoBD != '') {
        value = getValueFromData(data, elementConfig.campoBD);
      } else {
        value = elementConfig.value;
      }

      if (value !== null) {
        elementConfig.value = value;
        const elementDiv = document.getElementById(`${side}-${elementId}`);
        if (elementDiv) {
          const valueDiv = elementDiv.querySelector('.value');
          if (valueDiv) {
            valueDiv.innerHTML = value + ' ' + elementConfig.unit;
          }

          // comprobar condiciones en sideBlock
          if (elementConfig.avisos) {
            //console.log('Aviso.side',elementConfig.avisos);
            Object.keys(elementConfig.avisos).forEach((key) => {
              const aviso = elementConfig.avisos[key];

              const condicion = new Function(
                'value',
                'data',
                'now',
                `return ${aviso.condicion};`
              );

              //console.log(key,' -Evaluando condicion', aviso.condicion);
              if (condicion(value, data, now)) {
                if (aviso.color) elementDiv.style.backgroundColor = aviso.color; //por compatibilidad
                if (aviso.backgroundColor)
                  elementDiv.style.backgroundColor = aviso.backgroundColor;
                if (aviso.size) elementDiv.style.fontSize = aviso.size;
                if (aviso.bold) elementDiv.style.fontWeight = aviso.bold;
                if (aviso.width) elementDiv.style.width = `${aviso.width}px`;
                if (aviso.valueColor) {
                  //Color texto
                  const valueDiv = elementDiv.querySelector('.value');
                  if (valueDiv) valueDiv.style.color = aviso.valueColor; // Cambiar el color del valor
                }
              }
            });
          }
        }
      }
    });
  }

  if (config.laterales.izquierdo) {
    updateSideBlock(config.laterales.izquierdo, 'izquierdo');
  }

  if (config.laterales.derecho) {
    updateSideBlock(config.laterales.derecho, 'derecho');
  }
}

function createSideBlockElement(container, elementConfig, elementId, side) {
  const elementDiv = document.createElement('div');

  elementDiv.id = `${side}-${elementId}`;

  elementDiv.className = 'side-element';

  elementDiv.style.position = 'relative';
  elementDiv.style.width = `${elementConfig.width}px`;
  elementDiv.style.backgroundColor = elementConfig.backgroundColor;
  elementDiv.style.color = elementConfig.valueColor;
  elementDiv.style.fontSize = elementConfig.size;

  // Valores por defecto
  if (elementConfig.bold) elementDiv.style.fontWeight = 'bold';

  const title = document.createElement('div');

  // Verificar el atributo showTitle y mostrar el título si corresponde
  if (elementConfig.showTitle !== false) {
    const title = document.createElement('div');
    title.innerText = elementId + ': ';
    title.style.color = elementConfig.titleColor;
    elementDiv.appendChild(title);
  }

  const value = document.createElement('div');
  value.className = 'value';

  if (!elementConfig.unit) elementConfig.unit = '';

  value.innerText = elementConfig.value + ' ' + elementConfig.unit;
  //value.style.fontSize = elementConfig.size;
  //value.style.color = elementConfig.valueColor;
  elementDiv.appendChild(value);

  container.appendChild(elementDiv);
}

function getValueFromData_1(data, dbField) {
  const keys = dbField.split('.');
  let value = data;
  for (const key of keys) {
    value = value[key];
    if (value === undefined) {
      return null;
    }
  }
  return value;
}

function getValueFromData(data, campoBD) {
  const keys = campoBD.split('.');
  let value = data;
  for (let key of keys) {
    if (value[key] !== undefined) {
      value = value[key];
    } else {
      return null;
    }
  }
  return value;
}

function showModal(blockConfig, blockId) {
  if (activeModals[blockId]) return;

  const modalDiv = document.createElement('div');
  modalDiv.className = 'modal';

  // Obtener el bloque y sus coordenadas
  const blockDiv = document.getElementById(blockId);
  const rect = blockDiv.getBoundingClientRect();

  // Posicionar el modal cerca del bloque
  const offset = 10; // Desplazamiento en píxeles
  modalDiv.style.top = `${
    rect.top + window.scrollY + blockDiv.offsetHeight + offset
  }px`;
  modalDiv.style.left = `${rect.left + window.scrollX}px`;

  // Crear el encabezado del modal para arrastrar
  const headerDiv = document.createElement('div');
  headerDiv.className = 'modal-header';

  const titleSpan = document.createElement('span');
  titleSpan.innerHTML = `&nbsp;${blockId}&nbsp;`;
  titleSpan.className = 'modal-title';

  const closeButton = document.createElement('div');
  closeButton.innerHTML = `&nbsp;X&nbsp;`;
  closeButton.className = 'modal-close';
  closeButton.addEventListener('click', () => {
    document.body.removeChild(modalDiv);
    delete activeModals[blockId]; // Eliminar de las ventanas activas al cerrar
  });

  headerDiv.appendChild(titleSpan);
  headerDiv.appendChild(closeButton);
  modalDiv.appendChild(headerDiv);

  // Parte de Avisos a nivel Bloque
  const modalavisoDiv = document.createElement('div');
  modalavisoDiv.id = `MA-${blockId}`;
  modalavisoDiv.innerText = '';
  modalDiv.appendChild(modalavisoDiv);

  Object.keys(blockConfig.elements).forEach((elementId) => {
    const elementConfig = blockConfig.elements[elementId];
    if (elementConfig.visualizacion != 'nunca') {
      const elementDiv = document.createElement('div');
      elementDiv.id = `M-${blockId}-${elementId}`;

      let value = elementConfig.value;

      if (typeof value === 'number') {
        value = value.toLocaleString('de-DE', {
          minimumFractionDigits: 0,
          maximumFractionDigits: 3,
        });
      }

      let salida = `<span style="color: red">${elementId}:</span> <span style="color: black">${value} ${elementConfig.unit}</span>`;

      elementDiv.innerHTML = salida;

      modalDiv.appendChild(elementDiv);
    }
  });

  document.body.appendChild(modalDiv);

  // Registrar la ventana modal activa
  activeModals[blockId] = {
    modalContainer: modalDiv,
    blockConfig: blockConfig,
  };

  // Hacer la ventana modal arrastrable
  makeDraggable(modalDiv);

  fetchAndUpdateData();
}

function updateModalValues(data) {
  const d_ = Object.assign({}, data);

  const now = new Date(); // Hora actual
  Object.keys(activeModals).forEach((blockId) => {
    const modal = activeModals[blockId];
    const blockConfig = modal.blockConfig;

    // Avisos de bloque
    if (blockConfig.avisos) {
      //console.log('Avisos Bloque',blockId, blockConfig.avisos);

      const elementDiv = document.getElementById(`MA-${blockId}`);

      let salida = '';
      Object.keys(blockConfig.avisos).forEach((key) => {
        const aviso = blockConfig.avisos[key];

        const condicion = new Function(
          'd_',
          'now',
          `return ${aviso.condicion};`
        );

        if (condicion(data, now)) {
          salida += `<br><span style="color: brown">&emsp;- AVISO BLOQUE ${key}- </span>`;
          salida += `<span style="color: blue">${aviso.condicion}</span>`;
        }
      });
      if (salida != '')
        salida += `<br><span style="color: black">===============</span><br>`;

      elementDiv.innerHTML = salida;
    }

    Object.keys(blockConfig.elements).forEach((elementId) => {
      const elementConfig = blockConfig.elements[elementId];
      if (elementConfig.visualizacion != 'nunca') {
        let value = null;
        if (elementConfig.sensor) value = eval(elementConfig.sensor);
        else if (elementConfig.campoBD)
          value = getValueFromData(data, elementConfig.campoBD);

        //console.log('elementId:',elementId,' - value', value);

        const elementDiv = document.getElementById(`M-${blockId}-${elementId}`);
        if (elementDiv && value != null) {
          let value_adap = value;
          if (typeof value === 'number') {
            value_adap = value.toLocaleString('de-DE', {
              minimumFractionDigits: 0,
              maximumFractionDigits: 3,
            });
          }

          let salida = `<span style="color: red">${elementId}:</span> <span style="color: black">${value_adap} ${elementConfig.unit}</span>`;

          // Verificar avisos y mostrar condicion de aviso
          if (elementConfig.avisos) {
            const blockDiv = document.getElementById(blockId);

            Object.keys(elementConfig.avisos).forEach((key) => {
              const aviso = elementConfig.avisos[key];
              const condicion = new Function(
                'value',
                'data',
                'now',
                `return ${aviso.condicion};`
              );

              if (condicion(value, data, now)) {
                salida += `<br><span style="color: magenta">&emsp;${key}-> </span>`;
                salida += `<span style="color: blue">${aviso.condicion}</span>`;
              }
            });
          }

          elementDiv.innerHTML = salida;
        }
      }
    });
  });
}
