import time
import board

import adafruit_mlx90640

import busio
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import zoom

# Inicializar I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicializar sensor AMG8833
sensor = adafruit_mlx90640.MLX90640(i2c)

# Configuración de interpolación
# Factor de escalado para aumentar la resolución
INTERPOLATION_FACTOR = 1 # Aumenta la matriz 8x8 a 64x64

# Función para interpolar datos
def interpolar_datos(datos, factor):
    """
    Interpola los datos usando zoom bicúbico.
    """
    return zoom(datos, factor, order=3)  # order=3 -> Interpolación bicúbica

# Función principal para visualización en tiempo real
def visualizar_temperatura():
    """
    Visualiza el mapa térmico con interpolación en tiempo real.
    """
    plt.ion()  # Habilitar modo interactivo
    fig, ax = plt.subplots()

    # Datos iniciales para configurar el gráfico
    datos_iniciales = np.zeros((24, 32))  # Matriz inicial vacía
    datos_interpolados = interpolar_datos(datos_iniciales, INTERPOLATION_FACTOR)

    # Configuración del gráfico
    heatmap = ax.imshow(datos_interpolados, cmap="inferno", interpolation="bicubic")
    #heatmap = ax.imshow(datos_interpolados, cmap="viridis", interpolation="bicubic")

    plt.colorbar(heatmap, ax=ax)

    while True:
        try:
            # Leer datos del sensor
            
            mlx_frame = np.zeros(24 * 32)
            sensor.getFrame(mlx_frame)
            print('=' *80)
            
            #datos_crudos = np.reshape(mlx_frame, (24, 32))  # Redimensionar el frame de MLX90640
            datos_crudos = np.round(np.reshape(mlx_frame, (24, 32)), 1)
            
            
            # Imprimir fila por fila
            for fila in datos_crudos:
                print(" ".join(f"{x:5.1f}" for x in fila))  # Ajusta el formato si es necesario
            #print(datos_crudos)
            print()
            # Interpolar los datos
            datos_interpolados = interpolar_datos(datos_crudos, INTERPOLATION_FACTOR)
            
            #print ('lectura AGM interpolados',datos_interpolados)
            #time.sleep(5)

            #print(datos_interpolados)
            # Actualizar el mapa térmico
            heatmap.set_data(datos_interpolados)
            #heatmap.set_clim(vmin=datos_crudos.min(), vmax=datos_crudos.max())
            heatmap.set_clim(vmin=27, vmax=35)

            plt.draw()
            plt.pause(0.5)  # Actualizar cada 100 ms
        except KeyboardInterrupt:
            print("Lectura detenida.")
            break

if __name__ == "__main__":
    visualizar_temperatura()
