import matplotlib.pyplot as plt
from .interpolacion import interpolacion
from pathlib import Path


def graficar(
    x,
    y,
    label_1="NIST",
    x_comp=None,
    y_comp=None,
    label_2="Otro",
    nombre_x=None,
    nombre_y=None,
    unidad_x=None,
    unidad_y=None,
    interpolar=True,
    color="m",
    linewidth=1,
    markersize=40,
    carpeta: Path | str | None = None,
):
    """
    Grafica uno o dos sets de datos (x, y) como puntos y, opcionalmente, sus
    curvas interpoladas.

    El set principal (x, y) se dibuja con hexágonos del color elegido. Si se
    pasan x_comp e y_comp, se agrega un segundo set de comparación con círculos
    azules, de la mitad del tamaño, y se muestra una leyenda con label_1 y
    label_2 para identificar cada set. Con un solo set no se muestra leyenda.

    Si interpolar es "True", se agrega su curva interpolada: un spline
    cuadrático evaluado cada 0.05 entre el primer y el último valor de x.
    La del set principal es una línea continua y la del set de comparación,
    una línea punteada.

    Si se pasan los nombres y las unidades de las dos variables, el gráfico se
    titula y se guarda como PNG en la carpeta "Graficos" (se crea si no
    existe). Si falta alguno, se muestra con ejes genéricos y no se guarda.

    Parámetros:
        x, y : array
            Datos del set principal.
        label_1 : str, opcional
            Nombre del set principal en la leyenda. Por defecto, "NIST".
        x_comp, y_comp : array, opcional
            Datos del set de comparación. Si no se pasan, se grafica solo el
            set principal.
        label_2 : str, opcional
            Nombre del set de comparación en la leyenda. Si no se pasa, ese set
            no aparece en la leyenda.
        nombre_x, nombre_y : str, opcional
            Nombres de las variables, para los ejes, el título y el nombre del
            archivo.
        unidad_x, unidad_y : str, opcional
            Unidades de las variables, para los ejes.
        interpolar : bool, opcional
            Si es True (por defecto), dibuja las curvas interpoladas. Si es
            False, solo los puntos.
        color : str, opcional
            Color del set principal. Por defecto, magenta.
        linewidth : float, opcional
            Grosor de las curvas interpoladas de los dos sets.
        markersize : float, opcional
            Tamaño de los puntos del set principal. Los del set de comparación
            miden la mitad.
        carpeta : Path, str, None, opcional
            Ruta a la carpeta donde se desea guardar la figura generada. Por
            defecto se guarda en la carpeta 'Graficos' en la raíz (se crea si
            no existe).
    """

    if interpolar:
        curva_x, curva_y = interpolacion(x, y, espaciado=0.05)
        plt.plot(curva_x, curva_y, linewidth=linewidth, color=color)

    plt.scatter(
        x, y, marker="h", color=color, s=markersize, alpha=0.6, label=label_1
    )

    try:
        if interpolar:
            curva_comp_x, curva_comp_y = interpolacion(
                x_comp, y_comp, espaciado=0.05
            )
            plt.plot(
                curva_comp_x,
                curva_comp_y,
                linewidth=linewidth,
                linestyle="dashed",
                color="b",
            )
        plt.scatter(
            x_comp,
            y_comp,
            marker="o",
            color="b",
            s=markersize / 2,
            alpha=0.6,
            label=label_2,
        )
        plt.legend()
    except TypeError, ValueError:
        pass

    plt.grid(alpha=0.7, linestyle="--")

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
        plt.title(
            f"{nombre_y.capitalize()} vs. {nombre_x.lower()},"
            f" para valores entre {x[0]:.2f} y {x[-1]:.2f}"
        )
        if carpeta is None:
            carpeta = Path("Graficos")
        elif isinstance(carpeta, str):
            carpeta = Path(carpeta)
        elif not isinstance(carpeta, Path):
            raise TypeError("Variable 'carpeta' es no-válido")

        carpeta.mkdir(parents=True, exist_ok=True)
        nombre_archivo = (
            f"{nombre_y.lower()}_vs_{nombre_x.lower()}_"
            f"rango_{x[0]:.2f}_{x[-1]:.2f}.png"
        )
        plt.savefig(carpeta / nombre_archivo)

    plt.show()
