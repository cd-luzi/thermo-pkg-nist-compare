import CoolProp.CoolProp as CP
from CoolProp.CoolProp import PhaseSI
from thermo_pkg_nist_compare import PropData
import numpy as np


def main():
    model_disp = {"IAPWS95": "Water", "IAPWS-97": "IF97::Water"}
    # modelo = "IAPWS-97"
    # Para pruebas rápidas, se puede cambiar a "IAPWS-97"

    modelo = elegir_modelo(model_disp)

    P = np.linspace(1e4, 1e5, 10) / 1000  # kPa

    T = np.linspace(300, 400, 10)  # K

    try:
        u = (
            CP.PropsSI("Umass", "P", P * 1000, "T", T, model_disp[modelo])
            / 1000
        )  # kJ/(kg K)
        h = (
            CP.PropsSI("Hmass", "P", P * 1000, "T", T, model_disp[modelo])
            / 1000
        )  # kJ/kg
        s = (
            CP.PropsSI("Dmass", "P", P * 1000, "T", T, model_disp[modelo])
            / 1000
        )  # kJ/kg
    except Exception as e:
        raise Exception("""
        Algo falló en el llamado a CoolProp. Revisar la instalación o
        contactarse con los desarroladores.
        """) from e

    try:
        encabezados = ["T", "P", "u", "h", "s"]
        unidades = {
            "T": "K",
            "P": "kPa",
            "u": "kJ/kg",
            "h": "kJ/kg",
            "s": "kJ/kg*K",
        }

        tabla = PropData(
            datos=np.column_stack((T, P, u, h, s)),
            encabezados=encabezados,
            unidades=unidades,
        )

    except Exception as e:
        raise Exception("""
        Algo falló en el armado de la tabla final (PropData). Revisar la
        instalación o contactarse con los desarroladores.
        """) from e

    try:
        fases = [
            PhaseSI("P", float(p) * 1000, "T", float(t), model_disp[modelo])
            for p, t in zip(P, T)
        ]
    except Exception as e:
        raise Exception("""
        Algo falló en el llamado a PhaseSI (CoolProp). Revisar la instalación o
        contactarse con los desarroladores.
        """) from e

    tabla["Fase"] = fases

    tabla.unidades["Fase"] = ""

    print("\n", tabla, "\n")


def elegir_modelo(model_disp: dict[str:str]) -> str:
    intentos = 3
    while intentos > 0:
        modelo = input("Ingrese el modelo a usar (IAPWS95 o IAPWS-97): ")

        if modelo not in model_disp:
            print("""
            Modelo no válido. Debe ser 'IAPWS95' o 'IAPWS-97'.
            Intente nuevamente.
            """)
            intentos -= 1
        else:
            return modelo

    raise ValueError("Modelo no válido. Debe ser 'IAPWS95' o 'IAPWS-97'.")


if __name__ == "__main__":
    main()
