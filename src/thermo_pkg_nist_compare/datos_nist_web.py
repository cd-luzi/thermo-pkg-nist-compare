import re
from io import StringIO

import pandas as pd
import numpy as np
import requests

# ==========================================
# Parámetros constantes que se emplean en la
# construcción de los link según cada caso.
# ==========================================

URL_BASE = "https://webbook.nist.gov/cgi/fluid.cgi"

PARAMETROS_FIJOS: dict[str, str] = {
    "Action": "Data",
    "Wide": "on",
    "ID": "C7732185",
    "RefState": "DEF",
}

PARAMETROS_UNIDADES = {
    "TUnit": "K",
    "PUnit": "MPa",
    "DUnit": "kg/m3",
    "HUnit": "kJ/mol",
    "WUnit": "m/s",
    "VisUnit": "uPa*s",
    "STUnit": "N/m",
}


"""
Temperature (K)	Pressure (MPa)	Density (kg/m3)	Volume (m3/kg)	Internal Energy (kJ/kg)	Enthalpy (kJ/kg)	Entropy (J/g*K)	Cv (J/g*K)	Cp (J/g*K)	Sound Spd. (m/s)	Joule-Thomson (K/MPa)	Viscosity (uPa*s)	Therm. Cond. (W/m*K)	Phase

"""

class NISTData(pd.DataFrame):
    """
    Clase básica que hereda todo de DataFrame de pandas, pero que
    modifica el método __getitem__ para que devuelva directamente 
    un array de numpy cuando se pide por nombre.
    """

    def __getitem__(self, key):
        result = super().__getitem__(key)

        if isinstance(result, pd.Series):
            return result.to_numpy()

        return result


def main() -> None:

    data_table = busqueda_web(
        iso_var="IsoBar",
        iso_value=0.1,
        rg_min=373,
        rg_max=573,
        rg_interval=20,
    )

    print(data_table.to_string(index=False))
    print("Probando el retorno de una columna por nombre:")
    print("filas 2-5 de temperatura: ")
    for val in data_table["Temperature (K)"][2:6]:
        print(f" * T = {val}")
    return data_table


# Función principal de búsqueda
def busqueda_web(
    iso_var: str,
    iso_value: float,
    rg_min: float,
    rg_max: float,
    rg_interval: float,
    decimales: int = 12,
):

    parametros = validar_entradas(
        iso_var,
        iso_value,
        rg_min,
        rg_max,
        rg_interval,
        decimales,
    )

    try:
        consulta = requests.get(URL_BASE, params=parametros)
        consulta.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(consulta.url)
        print("HTTP error:", e)

    texto = consulta.text.splitlines()

    encabezados = texto[0]
    encabezados = re.split(r'(?<=\))\s+', encabezados)

    tabla_intermedia = pd.read_csv(
        StringIO("\n".join(texto[1:])),
        sep=r"\s+",
        names=encabezados,
        dtype={"Phase": str},
        engine="python",
    )

    return NISTData(tabla_intermedia)


# Validación de datos y creación de links para buscar
# datos isobáricos o isotérmicos
def validar_entradas(
    iso_var: str,
    iso_value: float,
    rg_min: float,
    rg_max: float,
    rg_interval: float,
    digitos: int,
) -> dict:

    match iso_var:
        case "IsoBar":
            # Luego validaremos el resto

            parametros_variables = {
                "Type": "IsoBar",
                "Digits": digitos,
                "P": iso_value,
                "TLow": rg_min,
                "THigh": rg_max,
                "TInc": rg_interval,
            }
        case "IsoTherm":
            # Luego validaremos el resto

            parametros_variables = {
                "Type": "IsoTherm",
                "Digits": digitos,
                "T": iso_value,
                "PLow": rg_min,
                "PHigh": rg_max,
                "PInc": rg_interval,
            }

        case _:
            raise ValueError(
                "'iso_var' debe ser 'IsoBar' o 'IsoTherm', "
                f"pero se ingresó el valor: {iso_var}"
            )

    return {**PARAMETROS_FIJOS, **PARAMETROS_UNIDADES, **parametros_variables}


if __name__ == "__main__":
    main()
