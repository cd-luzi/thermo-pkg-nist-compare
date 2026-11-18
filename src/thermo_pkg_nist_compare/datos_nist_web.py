import re
from io import StringIO

import pandas as pd
import requests

# =============================================================================
# Parámetros "constantes" que se emplean en el módulo. Como son de uso interno,
# antecedemos el símbolo "_" que es la convención usual. Los cuatro primeros
# están vinculados a la construcción de los link según cada caso.
# El último está vinculado a la clase definida para las tablas.
# =============================================================================

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


class NISTData(pd.DataFrame):
    """
    Clase básica que hereda todo de DataFrame de pandas, pero que
    modifica el método __getitem__ para que devuelva directamente
    un array de numpy cuando se pide por nombre.
    Además, desde los alias de base (_ALIAS_BASE), asigna alias a
    las distintas variables, para identificarlas más fácil (ver
    "_generate_aliases"). Los alias de base usados son:
        * "T": "Temperature"
        * "P": "Pressure"
        * "rho": "Density"
        * "v": "Volume"
        * "u": "Internal Energy"
        * "h": "Enthalpy"
        * "s": "Entropy"
        * "Cv": "Cv"
        * "Cp": "Cp"
        * "w": "Sound Spd."
        * "JT": "Joule-Thomson"
        * "mu": "Viscosity"
        * "k": "Therm. Cond."
        * "ph": "Phase"

        Y "_generate_aliases" los usa para crear la lista de alias definitivos
        para que coincidan con los nombres extraídos del NIST que agregan
        información sobre las unidades.
        Se puede acceder a la lista de alias completa con:
        self.alias
    """

    # Atributos personalizados que pandas conserva al crear copias o subconjuntos.
    # La tupla —("alias",)— evita usar una lista mutable —["alias"]— como atributo
    # de clase.
    _metadata = ("alias",)

    def __init__(self, data):

        super().__init__(data)

        self._generate_aliases(
            self.columns,
        )

    @property
    def _constructor(self):
        """
        Con esto nos garantizamos que las operaciones que devolverían un
        DataFrame de pandas nos sigan devolviendo la clase así definida. De
        esta manera, si data_table es una tabla creada con NISTData, la
        operación data_table[["T", "P"]] devolverá una clase NISTData en
        lugar de un DataFrame puro.
        """
        return NISTData

    def _generate_aliases(self, encabezados):

        aliases = {}

        for alias, name in _ALIAS_BASE.items():
            matches = [
                encabezado
                for encabezado in encabezados
                if name.casefold() == encabezado.split("(")[0].strip().casefold()
            ]

            if len(matches) == 1:
                aliases[alias] = matches[0]

        self.alias = aliases

    def __getitem__(self, keys):

        if isinstance(keys, list):
            keys = [self.alias.get(k, k) if isinstance(k, str) else k for k in keys]

        if isinstance(keys, str):
            keys = self.alias.get(keys, keys)

        result = super().__getitem__(keys)

        if isinstance(result, pd.Series):
            return result.to_numpy()

        return result


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

    return data_table


# Función principal de búsqueda
def busqueda_web_nist(
    iso_var: str,
    iso_value: float,
    rg_min: float,
    rg_max: float,
    rg_interval: float,
    decimales: int = 12,
):
    """Descarga datos termodinámicos del agua desde el WebBook del NIST.

    Parameters
    ----------
    iso_var : str
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
    NISTData
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

    return NISTData(
        pd.read_csv(
            StringIO("\n".join(texto[1:])),
            sep=r"\s+",
            names=encabezados,
            dtype={"Phase": str},
            engine="python",
        )
    )


# Validación de datos y creación de links para buscar
# datos isobáricos o isotérmicos
def validar_entradas_y_crear_parametros(
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
