from thermo_pkg_nist_compare import tabular
import numpy as np
import os

no_proxy = os.environ.get("NO_PROXY", os.environ.get("no_proxy", ""))
direcciones = [item.strip() for item in no_proxy.split(",") if item.strip()]
existentes = {item.casefold() for item in direcciones}

for host in ("localhost", "127.0.0.1", "::1"):
    if host.casefold() not in existentes:
        direcciones.append(host)

os.environ["NO_PROXY"] = ",".join(direcciones)


def main():
    x = np.array([0, 1, 2, 3, 4])
    y = np.array([0, 0.8, 0.9, 0.1, -0.8])

    try:
        tabular(
            x,
            y,
            comienzo=0,
            fin=5,
            espaciado=0.5,
            decimales=1,
            nombre_x="temperatura",
            nombre_y="presion",
            unidad_x="°C",
            unidad_y="Pa",
            carpeta="./examples/Tablas",
        )
    except Exception as e:
        raise Exception("""
        Algo falló. Revisar la instalación o contactarse con
        los desarroladores.
        """) from e
    else:
        print("Prueba exitosa, ver salida en la carpeta './examples/Tablas'.")


if __name__ == "__main__":
    main()
