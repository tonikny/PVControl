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

compensation_matrix = np.loadtxt("matriz_compensacion.csv", delimiter=",")
print(compensation_matrix)

while True:
    frame = np.zeros((24 * 32,))
    mlx.getFrame(frame)
    frame_matrix = np.reshape(frame, (24, 32))

    # Aplicar la compensacion
    corrected_frame = frame_matrix - compensation_matrix
    
    print(corrected_frame)
    # Mostrar la imagen corregida
    plt.imshow(corrected_frame, cmap="inferno")
    plt.colorbar()
    plt.title("Imagen Corregida")
    plt.show()
    time.sleep(1)
