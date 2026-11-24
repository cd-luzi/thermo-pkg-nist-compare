from graficadora import graficar
import numpy as np

x = np.array([0, 1, 2, 3, 4])
y = np.array([0, 0.8, 0.9, 0.1, -0.8])

x_2 = np.array([0, 1.5, 1.7, 3.5, 3.9])
y_2 = np.array([0.1, 0.85, 0.89, -0.4, -0.7])

graficar(x, y, x_comp=x_2, y_comp=y_2, label_2="CoolProp", nombre_x="temperatura", nombre_y="presion", unidad_x="°C", unidad_y="Pa", color='brown', linewidth=0.7, markersize=80)