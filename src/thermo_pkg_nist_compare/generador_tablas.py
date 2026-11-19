import numpy as np
from interpolacion import interpolacion
from pathlib import Path
import pandas as pd
from great_tables import GT

#pip install great_tables
def tabular(x, y, comienzo=None, fin=None, espaciado=None, decimales=3, nombre_x=None, nombre_y=None, unidad_x=None, unidad_y=None):
    """
    Genera una tabla con valores interpolados de (x, y) y la guarda como imagen.

    Interpola con un spline cuadrático desde `comienzo` cada `espaciado`, sin pasarse de `fin`, incluyéndolo.
    Por defecto: comienzo=x[0], fin=x[-1], espaciado=(fin-comienzo)/20.
    `decimales` fija cuántos decimales se muestran en la tabla.

    Si se pasan nombres y unidades de las variables, guarda la tabla como PNG
    en la carpeta "Tablas". Si falta alguno, no la gguarda, solo la genera.
    """
    if not(espaciado):
        espaciado = abs((x[0]-x[-1])/20)

    valores_x, valores_y = interpolacion(x, y, comienzo, fin, espaciado)

    guardar = True

    try:
        nombre_x = nombre_x.strip()
        nombre_y = nombre_y.strip()
    except AttributeError:
        nombre_x, nombre_y = "Variable x", "Variable y"
        unidad_x = unidad_y = "u.a."
        guardar = False
        print("Agregar nombre de las variables. No se generó la tabla.")
    else:
        try:
            unidad_x = unidad_x.strip()
            unidad_y = unidad_y.strip()
        except AttributeError:
            unidad_x = unidad_y = "u.a."
            guardar = False
            print("Agregar unidades. No se generó la tabla.") 

    variable_x = f"{nombre_x.capitalize()} [{unidad_x}]"
    variable_y = f"{nombre_y.capitalize()} [{unidad_y}]"

    df = pd.DataFrame({
        variable_x: valores_x,
        variable_y: valores_y,
        })
            
    tabla = (
        GT(df)
        .tab_header(title=f"{nombre_x.capitalize()} y {nombre_y.lower()} para valores entre {valores_x[0]} y {valores_x[-1]}")
        .fmt_number(columns=[variable_x, variable_y], decimals = decimales)
        )

    tabla.show()

    if guardar:   
        carpeta = Path("Tablas")
        carpeta.mkdir(parents=True, exist_ok=True)
        nombre_archivo = f"{nombre_y.lower()}_{nombre_x.lower()}_rango_{valores_x[0]}_{valores_x[-1]}.png"
        tabla.save(carpeta / nombre_archivo)  


