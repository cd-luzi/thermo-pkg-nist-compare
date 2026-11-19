import re

import requests

from thermo_pkg_nist_compare.propdata import PropData
from thermo_pkg_nist_compare.substancelist import Substance

# =============================================================================
# Parámetros "constantes" que se emplean en el módulo. Como son de uso interno,
# antecedemos el símbolo "_" que es la convención usual. Los cuatro primeros
# están vinculados a la construcción de los link según cada caso.
# El último está vinculado a la clase definida para las tablas.
# =============================================================================

# BUSCAR retry
# Agregar búsqueda isocórica (Type=IsoChor)
# Agregar caso de saturación: (Type=SatP o Type=SatT)


URL_BASE = "https://webbook.nist.gov/cgi/fluid.cgi"

PARAMETROS_FIJOS: dict[str, str] = {
    "Action": "Data",
    "Wide": "on",
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

_ALIAS_BASE = {
    "T": "Temperature",
    "P": "Pressure",
    "rho": "Density",
    "v": "Volume",
    "u": "Internal Energy",
    "h": "Enthalpy",
    "s": "Entropy",
    "Cv": "Cv",
    "Cp": "Cp",
    "w": "Sound Spd.",
    "JT": "Joule-Thomson",
    "mu": "Viscosity",
    "k": "Therm. Cond.",
    "ph": "Phase",
}

TIPOS_BUSQ = {
    "T cte": "IsoTherm",
    "T cte.": "IsoTherm",
    "IsoTherm": "IsoTherm",
    "Isotermico": "IsoTherm",
    "Isotérmico": "IsoTherm",

    "P cte": "IsoBar",
    "P cte.": "IsoBar",
    "IsoBar": "IsoBar",
    "Isobarico": "IsoBar",
    "Isobárico": "IsoBar",

    "V cte": "IsoChor",
    "V cte.": "IsoChor",
    "IsoChor": "IsoChor",
    "Isocorico": "IsoChor",
    "Isocórico": "IsoChor",

    "SatP": "SatP",
    "Saturacion P cte": "SatP",
    "Saturacion P cte.": "SatP",
    "Saturación P cte": "SatP",
    "Saturación P cte.": "SatP",

    "SatT": "SatT",
    "Saturacion T cte": "SatT",
    "Saturacion T cte.": "SatT",
    "Saturación T cte": "SatT",
    "Saturación T cte.": "SatT",
}

SUSTANCIA_POR_DEFECTO = Substance.from_alias("agua")

def main() -> None:
    """
    Todo lo que está acá sirve de ejemplo cuando se ejecuta el script con:

    uv run datos_nist_web.py

    Pero no se ejecutará cuando se importe "busqueda_web_nist"
    """

    data_table = busqueda_web_nist(
        iso_var="IsoBar",
        iso_value=0.1,
        rg_min=373,
        rg_max=573,
        rg_interval=20,
    )

    print("Impresión de la tabla de prueba completa:")
    print(data_table.to_string(index=False))
    print("\nProbando el retorno de una columna por nombre:")
    print("filas 2-5 de temperatura: ")
    for val in data_table["Temperature (K)"][2:6]:
        print(f" * T = {val}")

    print("\nImpresión de un extracto de la tabla con un subconjunto de propiedades:")
    table_red = data_table[["T", "P", "u", "h", "s"]]
    # La opción más larga según este ejemplo sería:
    """
    table_red = data_table[
        [
            "Temperature (K)",
            "Pressure (MPa)",
            "Internal Energy (kJ/mol)",
            "Enthalpy (kJ/mol)",
            "Entropy (J/mol*K)",
        ]
    ]
    """
    print(table_red)
    print(table_red["h"])
    print(data_table.alias)


# Función principal de búsqueda
def busqueda_web_nist(
    iso_var: str,
    iso_value: float,
    rg_min: float,
    rg_max: float,
    rg_interval: float,
    decimales: int = 12,
    sustancia: Substance = SUSTANCIA_POR_DEFECTO,
    unidades: dict[str, str] | None = None,
) -> PropData:
    """Descarga datos termodinámicos del agua desde el WebBook del NIST.

    Parameters
    ----------
    iso_var : str ACTUALIZAR!!!
        Tipo de búsqueda: "IsoBar" (presión fija) o "IsoTherm"
        (temperatura fija).
    iso_value : float
        Presión fija en MPa para "IsoBar" o temperatura fija en K
        para "IsoTherm".
    rg_min, rg_max, rg_interval : float
        Límites e intervalo de la variable que cambia: temperatura en K
        para "IsoBar" o presión en MPa para "IsoTherm".
    decimales : int, default 12
        Cantidad de dígitos solicitados al NIST.

    Returns
    -------
    Objeto PropData
        Tabla de resultados. Permite acceder a propiedades usando sus
        nombres completos o alias, por ejemplo, "Temperature (K)" o "T".

    Raises
    ------
    ValueError
        Si `iso_var` no es "IsoBar" ni "IsoTherm".

    Notes
    -----
    Mejoras previstas:
    - Permitir seleccionar otros fluidos disponibles en el WebBook además del
    agua.
    - Añadir más parámetros de entrada (opcionales) para indicar unidades u
    otras opciones de búsqueda.
    - Añadir opciones para guardar los datos descargados.
    """

    parametros = validar_entradas_y_crear_parametros(
        iso_var,
        iso_value,
        rg_min,
        rg_max,
        rg_interval,
        decimales,
        sustancia,
    )

    try:
        consulta = requests.get(URL_BASE, params=parametros)
        consulta.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(consulta.url)
        print("HTTP error:", e)

    texto = consulta.text.splitlines()

    encabezados = texto[0]
    encabezados = re.split(r"(?<=\))\s+", encabezados)
    datos = "\n".join(texto[1:])

    return PropData(datos, encabezados, _ALIAS_BASE)


# Validación de datos y creación de links para buscar
# datos isobáricos o isotérmicos
def validar_entradas_y_crear_parametros(
    iso_var: str,
    iso_value: float,
    rg_min: float,
    rg_max: float,
    rg_interval: float,
    digitos: int,
    sustancia: Substance,
) -> dict:

    # ACTUALIZAR ISOVAR!

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
                "ID": sustancia.nist_id
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
                "ID": sustancia.nist_id
            }

        case _:
            raise ValueError(
                "'iso_var' debe ser 'IsoBar' o 'IsoTherm', "
                f"pero se ingresó el valor: {iso_var}"
            )

    return {**PARAMETROS_FIJOS, **PARAMETROS_UNIDADES, **parametros_variables}


if __name__ == "__main__":
    main()
