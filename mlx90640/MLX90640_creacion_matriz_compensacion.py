#### script para calcular la mariz de compensacion del sensor termico MLX90640 si se detectan lineas regulares


import time
import numpy as np
import matplotlib.pyplot as plt
from adafruit_mlx90640 import MLX90640

# Configuracion del sensor MLX90640
import board
import busio
from adafruit_mlx90640 import RefreshRate

# Inicializacion del bus I2C y el sensor
i2c = busio.I2C(board.SCL, board.SDA)
mlx = MLX90640(i2c)
mlx.refresh_rate = RefreshRate.REFRESH_0_5_HZ  # Ajustar la frecuencia de muestreo si es necesario

# Parametros de captura
num_frames = 100  # Numero de imagenes a capturar
captured_frames = np.zeros((24, 32, num_frames))  # Almacenamiento de las capturas

print("Capturando imagenes para calcular la matriz ...")
time.sleep(2)

# Capturar varias imagenes
for i in range(num_frames):
    print(i)
    frame = np.zeros((24 * 32,))
    try:
        mlx.getFrame(frame)
    except ValueError:
        print(f"Error al capturar el frame {i + 1}, intentando de nuevo...")
        continue
    
    # Convertir el frame en una matriz de 24x32 y almacenarlo
    captured_frames[:, :, i] = np.reshape(frame, (24, 32))
    time.sleep(0.2)  # Esperar un poco entre capturas

# Calcular la media de cada pixel
pixel_means = np.mean(captured_frames, axis=2)
print('Media pixels: ',pixel_means)


# Calcular el valor promedio general de todos los pixeles
overall_mean = np.mean(pixel_means)
print('Media global: ',overall_mean)

# Calcular la matriz de offset
offset_matrix = overall_mean - pixel_means

# Redondear la matriz de offset existente a 2 decimales
offset_matrix = np.round(offset_matrix, 2)

# Guardar la matriz en un archivo
#np.savetxt("offset_matrix.csv", offset_matrix, delimiter=",")
np.savetxt("matriz_compensacion.csv", offset_matrix, delimiter=",", fmt="%+6.2f")
print("Matriz de compensacion calculada y guardada como 'matriz_compensacion.csv'.")

# Visualizar la matriz de offset
plt.imshow(offset_matrix, cmap="coolwarm")
plt.colorbar()
plt.title("Matriz de Compensacion (Desplazamientos)")
plt.show()
