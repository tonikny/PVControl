import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import zoom
from adafruit_mlx90640 import MLX90640

# Configuracion del sensor MLX90640
import board
import busio
from adafruit_mlx90640 import RefreshRate

# Inicializacion del bus I2C y el sensor
i2c = busio.I2C(board.SCL, board.SDA)
mlx = MLX90640(i2c)

mlx.refresh_rate = RefreshRate.REFRESH_0_5_HZ  # Frecuencia de muestreo
#mlx.refresh_rate = RefreshRate.REFRESH_1_HZ  # Frecuencia de muestreo
#mlx.refresh_rate = RefreshRate.REFRESH_2_HZ  # Frecuencia de muestreo
#mlx.refresh_rate = RefreshRate.REFRESH_4_HZ  # Frecuencia de muestreo

# Cargar la matriz de compensacion calculada previamente
offset_matrix = np.loadtxt("offset_matrix.csv", delimiter=",")

# Factores de interpolacion
zoom_factor = 4  # Aumenta la definicion a 4x

# Configuracion de la visualizacion en tiempo real
plt.ion()
fig, axs = plt.subplots(2, 2, figsize=(12, 10))

tmax = 35
tmin = 25
# Configuracion de los graficos
img_real = axs[0, 0].imshow(np.zeros((24, 32)), cmap="inferno", vmin=tmin, vmax=tmax)
axs[0, 0].set_title("Imagen Capturada Real")
plt.colorbar(img_real, ax=axs[0, 0])

img_corrected = axs[0, 1].imshow(np.zeros((24, 32)), cmap="inferno", vmin=tmin, vmax=tmax)
axs[0, 1].set_title("Imagen Capturada con Correccion")
plt.colorbar(img_corrected, ax=axs[0, 1])

img_real_interpolated = axs[1, 0].imshow(np.zeros((24 * zoom_factor, 32 * zoom_factor)), cmap="inferno", vmin=tmin, vmax=tmax)
axs[1, 0].set_title("Imagen Real Interpolada")
plt.colorbar(img_real_interpolated, ax=axs[1, 0])

img_corrected_interpolated = axs[1, 1].imshow(np.zeros((24 * zoom_factor, 32 * zoom_factor)), cmap="inferno", vmin=tmin, vmax=tmax)
axs[1, 1].set_title("Imagen Corregida e Interpolada")
plt.colorbar(img_corrected_interpolated, ax=axs[1, 1])

print("Mostrando capturas en tiempo real...")

# Bucle infinito para capturar y mostrar frames en tiempo real

try:
    while True:
        # Capturar un frame
        frame = np.zeros((24 * 32,))
        try:
            mlx.getFrame(frame)
        except ValueError:
            print("Error al capturar el frame, intentando de nuevo...")
            continue

        # Convertir el frame en una matriz de 24x32
        frame_matrix = np.reshape(frame, (24, 32))

        # Aplicar la compensacion
        corrected_frame = frame_matrix + offset_matrix

        # Interpolacion de las imagenes
        interpolated_real = zoom(frame_matrix, zoom_factor, order=3)  # Interpolacion bicubica
        interpolated_corrected = zoom(corrected_frame, zoom_factor, order=3)

        # Actualizar las imagenes en la visualizacion
        img_real.set_data(frame_matrix)
        img_corrected.set_data(corrected_frame)
        img_real_interpolated.set_data(interpolated_real)
        img_corrected_interpolated.set_data(interpolated_corrected)

        # Pausar brevemente para actualizar la visualizacion
        plt.pause(0.01)
except KeyboardInterrupt:
    print("Finalizando el programa.")
    plt.close()
