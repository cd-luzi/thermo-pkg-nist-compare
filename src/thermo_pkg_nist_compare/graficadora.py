import matplotlib.pyplot as plt
import numpy as np
from interpolacion import interpolacion
from pathlib import Path

def graficar(x, y, nombre_x=None, nombre_y=None, unidad_x=None, unidad_y=None, color='m', linewidth=1, markersize=40):
    """
    Grafica los datos (x, y) como puntos, junto con su curva interpolada.

    La curva sale de un spline cuadrático evaluado cada 0.05 entre x[0] y x[-1].
    Si se pasan nombres y unidades de las variables, guarda el gráfico como PNG
    en la carpeta "Graficos". Si falta alguno, lo muestra con ejes genéricos y no lo guarda.

    Se puede elegir color, linewidth y markersize para controlar el color, el grosor de la curva
    y el tamaño de los puntos.
    """
    curva_x, curva_y = interpolacion(x, y, espaciado=0.05)

    plt.plot(curva_x, curva_y, linewidth=linewidth, color=color)
    plt.scatter(x, y, marker='h', color=color, s=markersize, alpha=0.6)
    plt.grid(alpha=0.7, linestyle='--')

    guardar = True

    try:
        nombre_x = nombre_x.strip()
        nombre_y = nombre_y.strip()
    except AttributeError:
        nombre_x, nombre_y = "Eje x", "Eje y"
        unidad_x = unidad_y = "u.a."
        guardar = False
        print("Agregar nombre de las variables. No se guardó el gráfico.")
    else:
        try:
            unidad_x = unidad_x.strip()
            unidad_y = unidad_y.strip()
        except AttributeError:
            unidad_x = unidad_y = "u.a."
            guardar = False
            print("Agregar unidades. No se guardó el gráfico.")

    plt.xlabel(f"{nombre_x.capitalize()} [{unidad_x}]")
    plt.ylabel(f"{nombre_y.capitalize()} [{unidad_y}]")

    if guardar:
        plt.title(f"{nombre_y.capitalize()} vs. {nombre_x.lower()}, para valores entre {x[0]} y {x[-1]}")
        carpeta = Path("Graficos")
        carpeta.mkdir(parents=True, exist_ok=True)
        nombre_archivo = f"{nombre_y.lower()}_vs_{nombre_x.lower()}_rango_{x[0]}_{x[-1]}.png"
        plt.savefig(carpeta / nombre_archivo)

    plt.show()