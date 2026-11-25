from thermo_pkg_nist_compare import graficar
import numpy as np


def main():
    x = np.array([0, 1, 2, 3, 4])
    y = np.array([0, 0.8, 0.9, 0.1, -0.8])

    x_2 = np.array([0, 1.5, 1.7, 3.5, 3.9])
    y_2 = np.array([0.1, 0.85, 0.89, -0.4, -0.7])

    try:
        graficar(
            x,
            y,
            x_comp=x_2,
            y_comp=y_2,
            label_2="CoolProp",
            nombre_x="temperatura",
            nombre_y="presion",
            unidad_x="°C",
            unidad_y="Pa",
            color="brown",
            linewidth=0.7,
            markersize=80,
            carpeta="./examples/Graficos",
        )
    except Exception as e:
        raise Exception("""
        Algo falló. Revisar la instalación o contactarse con
        los desarroladores.
        """) from e
    else:
        print(
            "Prueba exitosa, ver salida en la carpeta './examples/Graficos'."
        )


if __name__ == "__main__":
    main()
