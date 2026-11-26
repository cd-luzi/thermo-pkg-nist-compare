import numpy as np
from .interpolacion import interpolacion
from pathlib import Path
import pandas as pd
from great_tables import GT
#probando

#pip install great_tables
def tabular(x, y, titulo_1="NIST", x_comp=None, y_comp=None, titulo_2="Otro",comienzo=None, fin=None, espaciado=None, decimales=3, nombre_x=None, nombre_y=None, unidad_x=None, unidad_y=None, interpolar=True):
    """
    Genera una tabla con uno o dos sets de datos (x, y), interpolados o tal cual.

    El set principal (x, y) ocupa las dos primeras columnas. Si se pasan x_comp e y_comp, se agrega
    un segundo set de comparación en dos columnas más, y cada set lleva arriba su
    subtítulo (titulo_1 y titulo_2) para identificarlo. Con un solo set no se muestran subtítulos.
    Si los sets tienen distinto largo, las celdas que sobran quedan vacías.

    Si interpolar es True, cada set se reemplaza por su interpolación: un spline cuadrático
    evaluado desde comienzo cada espaciado, hasta fin e incluyéndolo. Si es False,
    se usan los datos tal cual.

    Si se pasan los nombres y las unidades de las dos variables, la tabla se guarda como PNG
    en la carpeta "Tablas" (se crea si no existe), con las variables y el rango en el nombre del
    archivo. Si falta alguno, se muestra con encabezados genéricos y no se guarda.

    Parámetros:
        x, y : array
            Datos del set principal.
        titulo_1 : str, opcional
            Subtítulo del set principal. Por defecto, "NIST".
        x_comp, y_comp : array, opcional
            Datos del set de comparación. Si no se pasan, o tienen distinto largo entre sí,
            se tabula solo el set principal.
        titulo_2 : str, opcional
            Subtítulo del set de comparación. Por defecto, "Otro".
        comienzo : float, opcional
            Valor de x donde empieza la tabla. Por defecto, x[0].
        fin : float, opcional
            Valor de x donde termina la tabla, incluido. Por defecto, x[-1].
        espaciado : float, opcional
            Paso entre valores de x. Por defecto, |x[-1] - x[0]| / 20.
        decimales : int, opcional
            Cantidad de decimales que se muestran. Por defecto, 3.
        nombre_x, nombre_y : str, opcional
            Nombres de las variables, para los encabezados, el título y el nombre del archivo.
        unidad_x, unidad_y : str, opcional
            Unidades de las variables, para los encabezados.
        interpolar : bool, opcional
            Si es True (por defecto), tabula los valores interpolados. Si es False, se usan los datos originales.
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
            .tab_spanner(label=titulo_1, columns=["x_1", "y_1"])
            .tab_spanner(label=titulo_2, columns=["x_2", "y_2"])
            .sub_missing(missing_text="")
        )

    tabla.show()

    if guardar:   
        carpeta = Path("Tablas")
        carpeta.mkdir(parents=True, exist_ok=True)
        nombre_archivo = f"{nombre_y.lower()}_{nombre_x.lower()}_rango_{valores_x[0]}_{valores_x[-1]}.png"
        tabla.save(carpeta / nombre_archivo)  


