import numpy as np
from interpolacion import interpolacion
from pathlib import Path
import pandas as pd
from great_tables import GT

#pip install great_tables
def tabular(x, y, titulo_1="NIST", x_comp=None, y_comp=None, titulo_2="Otro" ,comienzo=None, fin=None, espaciado=None, decimales=3, nombre_x=None, nombre_y=None, unidad_x=None, unidad_y=None, interpolar=True):
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

    if interpolar:
        valores_x, valores_y = interpolacion(x, y, comienzo, fin, espaciado)
    else:
        valores_x, valores_y = x, y

    guardar = True

    try:
        if len(x_comp) != len(y_comp):
            raise ValueError("Distinto largo de las dos variables")
        if interpolar:
            valores_comp_x, valores_comp_y = interpolacion(x_comp, y_comp, comienzo, fin, espaciado)
        else:
            valores_comp_x, valores_comp_y = x_comp, y_comp
    except(TypeError, ValueError):
        comparar = False
    else:
        comparar = True

    try:
        nombre_x = nombre_x.strip()
        nombre_y = nombre_y.strip()
    except AttributeError:
        nombre_x, nombre_y = "Variable x", "Variable y"
        unidad_x = unidad_y = "u.a."
        guardar = False
        print("Agregar nombre de las variables. No se guardó la tabla.")
    else:
        try:
            unidad_x = unidad_x.strip()
            unidad_y = unidad_y.strip()
        except AttributeError:
            unidad_x = unidad_y = "u.a."
            guardar = False
            print("Agregar unidades. No se guardó la tabla.") 

    variable_x = f"{nombre_x.capitalize()} [{unidad_x}]"
    variable_y = f"{nombre_y.capitalize()} [{unidad_y}]"

    df = pd.DataFrame({
        "x_1": valores_x,
        "y_1": valores_y,
        })

    if comparar:

        variable_x_comp = f"{nombre_x.capitalize()} [{unidad_x}]"
        variable_y_comp = f"{nombre_y.capitalize()} [{unidad_y}]"

        df_comp = pd.DataFrame({
            "x_2": valores_comp_x,
            "y_2": valores_comp_y, 
        })

        df = pd.concat([df, df_comp], axis=1)
            
    tabla = (
        GT(df)
        .tab_header(title=f"{nombre_x.capitalize()} y {nombre_y.lower()} para valores entre {valores_x[0]} y {valores_x[-1]}")
        .fmt_number(columns=list(df.columns), decimals = decimales)
        .cols_label({"x_1":variable_x, "y_1":variable_y})
        )

    if comparar: 
        tabla = (
            tabla
            .cols_label({"x_2":variable_x_comp, "y_2":variable_y_comp})
            .tab_spanner(label=titulo_1, columns=[variable_x, variable_y])
            .tab_spanner(label=titulo_2, columns=[variable_x_comp, variable_y_comp])
            .sub_missing(missing_text="")
        )

    tabla.show()

    if guardar:   
        carpeta = Path("Tablas")
        carpeta.mkdir(parents=True, exist_ok=True)
        nombre_archivo = f"{nombre_y.lower()}_{nombre_x.lower()}_rango_{valores_x[0]}_{valores_x[-1]}.png"
        tabla.save(carpeta / nombre_archivo)  


