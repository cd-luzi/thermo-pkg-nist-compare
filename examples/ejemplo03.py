# Para hacer:
# Volcar un ejemplo básico de uso y testeo del generador de tablas.
# Similar (o igual a lo que está en el ipynb), pero
# pensado para el testeo rápido desde la línea de comandos de alguien
# que descargue el proyecto.

from thermo_pkg_nist_compare.generador_tablas import tabular
import numpy as np

x = np.array([0, 1, 2, 3, 4])
y = np.array([0, 0.8, 0.9, 0.1, -0.8])

tabular(x, y, comienzo=0, fin=5, espaciado=0.5, decimales=1, nombre_x="temperatura", nombre_y="presion", unidad_x="°C", unidad_y="Pa")