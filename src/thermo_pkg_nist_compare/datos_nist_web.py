import math

import re

import requests

import warnings

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

ALIAS_BASE = {
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

# Diccionario para definir el tipo de búsqueda, incorporando diferentes variantes
# que podría escribir el usuario. Como la búsqueda se hará sin tener en cuenta
# las mayúsculas usamos en cada clave `.casefold()`.
TIPOS_BUSQ = {
    "T cte".casefold(): "IsoTherm",
    "T cte.".casefold(): "IsoTherm",
    "IsoTherm".casefold(): "IsoTherm",
    "Isotermico".casefold(): "IsoTherm",
    "Isotérmico".casefold(): "IsoTherm",
    "P cte".casefold(): "IsoBar",
    "P cte.".casefold(): "IsoBar",
    "IsoBar".casefold(): "IsoBar",
    "Isobarico".casefold(): "IsoBar",
    "Isobárico".casefold(): "IsoBar",
    "V cte".casefold(): "IsoChor",
    "V cte.".casefold(): "IsoChor",
    "IsoChor".casefold(): "IsoChor",
    "Isocorico".casefold(): "IsoChor",
    "Isocórico".casefold(): "IsoChor",
    "SatP".casefold(): "SatP",
    "Saturacion P cte".casefold(): "SatP",
    "Saturacion P cte.".casefold(): "SatP",
    "Saturación P cte".casefold(): "SatP",
    "Saturación P cte.".casefold(): "SatP",
    "SatT".casefold(): "SatT",
    "Saturacion T cte".casefold(): "SatT",
    "Saturacion T cte.".casefold(): "SatT",
    "Saturación T cte".casefold(): "SatT",
    "Saturación T cte.".casefold(): "SatT",
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
    rg_min: float,
    rg_max: float,
    rg_interval: float,
    iso_value: float | None = None,
    decimales: int = 12,
    sustancia: Substance = SUSTANCIA_POR_DEFECTO,
    unidades: dict[str, str] | None = None,
) -> PropData:
    """Descarga datos termodinámicos del agua desde el WebBook del NIST.

    Parameters
    ----------
    iso_var: str
        Define el tipo de búsqueda. Formalmente puede ser:
          * "IsoBar"   (presión fija)
          * "IsoTherm" (temperatura fija)
          * "IsoChor"  (volumen fijo)
          * "SatP"     (Eq. líquido-vapor, presión a determinar —el rango dado
                        corresponde a la temperatura—)
          * "SatT"     (Eq. líquido-vapor, temperatura a determinar —el rango
                        dado corresponde a la presión—)
        Internamente se trabaja con alias para detectar otras formas esperables
        (por ejemplo, "T cte" e "Isotermico",  equivale a "IsoTherm"). Ver
        `datos_nist_web.TIPOS_BUSQ`.

    iso_value : float o None
        Presión fija en las unidades seleccionadas (MPa por defecto), si
        iso_var="IsoBar". Temperatura fija en las unidades seleccionadas (K por
        defecto), si iso_var="IsoTherm". Volumen  fijo en las unidades
        seleccionadas (m^3/kg por defecto), si iso_var="IsoChor". None o
        cualquier valor en caso contrario (no se utiliza).

    rg_min, rg_max, rg_interval: float
        Límites e intervalo de la variable que cambia, de acuerdo con la
        selección para `iso_var` y las unidades seleccionadas.

    decimales: int, opcional (default 12)
        Cantidad de dígitos solicitados al NIST. Debe ser un entero entre 5 y 12.

    sustancia: Substance, opcional (default, agua)
        Objeto `Substance`, que contiene información del ID para el NIST. Se
        crea con sustancia = Substance.from_alias("nombre"), donde nombre puede
        ser el nombre común de la sustancia en Español o en Inglés o la fórmula
        química (ejemplo: "agua", "water", "H2O"). El listado se puede consultar
        en el módulo substancelist.py.

    unidades: dict[str, str] o None (valor por defecto)
        Si se ingresa un diccionario, sus claves deben coincidir con algunas de
        las siguientes:
         * "TUnit":   unidades para la temperatura.
         * "PUnit":   unidades para la presión.
         * "DUnit":   unidades para la densidad (y por extensión, para el
                      volumen)
         * "HUnit":   unidades para los potenciales termodinámicos. Las unidades
                      de la entropía, los calores específicos, el coeficiente
                      Joule-Thomson y la conductividad térmica se derivan de
                      este, TUnit y PUnit.
         * "WUnit":   unidades para la velocidad del sonido
         * "VisUnit": unidades para la viscosidad
         * "STUnit":  unidades para la tensión superficial (solo en fase líquida
                      para los datos de equilibrio de fases)
        Cualquier otro par clave-valor se ignora.

    Returns
    -------
    Objeto(s) PropData
        Tabla de resultados creada con PropData. Permite acceder a propiedades
        usando sus nombres completos o alias (recomendado), por ejemplo,
        "Temperature (K)" o "T".
        Si se selecciona la búsqueda por presión o temperatura para los datos
        de saturación, devuelve dos tablas. La primera corresponde a la fase
        líquida y la segunda a la fase vapor (### Sin implementar aún)


    Notes
    -----
    Mejoras previstas si queda tiempo:
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

    return PropData(datos, encabezados, ALIAS_BASE)


# Validación de datos y creación de links para buscar
# datos isobáricos o isotérmicos
def validar_entradas_y_crear_parametros(
    iso_var: str,
    iso_value: float | None,
    rg_min: float,
    rg_max: float,
    rg_interval: float,
    digitos: int,
    sustancia: Substance,
) -> dict:

    # Determinación del valor adecuado de iso_var (puede resultar "None", en
    # cuyo caso se arroja un error en el bloque `match`).
    iso_var = get_case_insensitive(TIPOS_BUSQ, iso_var)

    # Comprobación sobre iso_value si corresponde:
    validar_numeros(iso_value, "iso_value", iso_var)

    # Comprobación sobre los restantes valores numéricos:
    validar_numeros(rg_min, "rg_min", None)
    validar_numeros(rg_max, "rg_max", None)
    validar_numeros(rg_interval, "rg_interval", None)

    # Validación de la cantidad de dígitos:
    digitos = validar_digitos(digitos)

    if not isinstance(sustancia, Substance):
        raise TypeError("`sustancia` debe pertenecer a la clase `Substance`.")

    match iso_var:
        case "IsoBar":
            parametros_variables = {
                "Type": "IsoBar",
                "Digits": digitos,
                "P": iso_value,
                "TLow": rg_min,
                "THigh": rg_max,
                "TInc": rg_interval,
                "ID": sustancia.nist_id,
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
                "ID": sustancia.nist_id,
            }

        case _:
            raise ValueError(f"""
                'iso_var' debe ser compatible con:\n"
                 * 'IsoBar'\n
                 * 'IsoTherm'\n
                 * 'IsoChor'\n
                 * 'SatP'\n
                 * 'SatT'\n
                pero se ingresó el valor: {iso_var}
                """)

    return {**PARAMETROS_FIJOS, **PARAMETROS_UNIDADES, **parametros_variables}


def validar_numeros(valor, nombre, iso_var):
    if nombre == "iso_value" and iso_var in {"SatP", "SatT"}:
        # Puede ser None o cualquier otra cosa, el valor no se usará. No es
        # necesario continuar con la validación
        return

    if valor is None:
        if iso_var is None:  # valor no se trata de iso_value.
            raise ValueError(f"{nombre} es obligatorio")
        elif iso_var in {"IsoBar", "IsoTherm", "IsoChor"}:
            if nombre == "iso_value":
                raise ValueError(f"iso_value es obligatorio para {iso_var}")
            else:
                # En rigor, si llegó hasta acá, va a fallar en la próxima comprobación.
                # De todas maneras, dejamos la impresión del warning, porque puede
                # ser informativo.
                warnings.warn(
                    f"""
                    La combinación {valor = }, {nombre = } y {iso_var = }\n
                    sugiere un error en la entrada. Se continúa con las comprobaciones...
                    """
                )

    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"{nombre} debe ser un número.")

    try:
        if valor < 0 or not math.isfinite(valor):
            raise ValueError(f"{nombre} debe ser finito y mayor o igual que cero.")
    except OverflowError:
        raise ValueError(f"{nombre} debe ser finito y mayor o igual que cero.")


def validar_digitos(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError("El número de dígitos debe ser numérico.")

    if (valor_ent := int(valor)) != valor:
        raise ValueError("El número de dígitos debe ser un número entero.")

    if not 5 <= valor_ent <= 12:
        raise ValueError("El número de dígitos debe estar entre 5 y 12.")

    return valor_ent


def get_case_insensitive(
    dictionary: dict[str, str],
    key: str,
) -> str | None:

    if key is None:
        return None

    if not isinstance(key, str):
        raise TypeError("Se esperaba un `str` o `None`.")

    return dictionary.get(key.casefold())


if __name__ == "__main__":
    main()
