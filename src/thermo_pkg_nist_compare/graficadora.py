import matplotlib.pyplot as plt
import numpy as np
from interpolacion import interpolacion
from pathlib import Path

def graficar(x, y, nombre_x=None, nombre_y=None, unidad_x=None, unidad_y=None, color='m', linewidth=1, markersize=40):

    curva_x, curva_y = interpolacion(x, y, espaciado=0.05)

    plt.plot(curva_x, curva_y, linewidth=linewidth, color=color)
    plt.scatter(x, y, marker='h', color=color, s=markersize, alpha=0.6)
    plt.grid(alpha=0.7, linestyle='--')

    if ((nombre_x is not None) & (nombre_y is not None)):
    
        nombre_x = nombre_x.strip()
        nombre_y = nombre_y.strip()

        if ((unidad_x is not None) & (unidad_y is not None)):

            unidad_x = unidad_x.strip()
            unidad_y = unidad_y.strip()
            plt.xlabel(f"{nombre_x.capitalize()} [{unidad_x}]")
            plt.ylabel(f"{nombre_y.capitalize()} [{unidad_y}]")
            plt.title(f"{nombre_y.capitalize()} vs. {nombre_x.lower()}, para valores entre {x[0]} y {x[-1]}")

            carpeta = Path("Graficos")
            carpeta.mkdir(parents=True, exist_ok=True)
            nombre_archivo = f"{nombre_y.lower()}_vs_{nombre_x.lower()}_rango_{x[0]}_{x[-1]}.png"
            plt.savefig(carpeta / nombre_archivo)
        else:
            unidad_x = "u.a."
            unidad_y = "u.a."
            print("Agregar unidades. No se guardó el grafico.")
    else:

        nombre_x = "Eje x"
        nombre_y = "Eje y"
        unidad_x = "u.a."
        unidad_y = "u.a."

        print("Agregar nombre de las variables. No se guardó el gráfico.")

    plt.xlabel(f"{nombre_x.capitalize()} [{unidad_x}]")
    plt.ylabel(f"{nombre_y.capitalize()} [{unidad_y}]")    

    plt.show()