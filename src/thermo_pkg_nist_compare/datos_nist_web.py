import math
import re
import warnings

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

UNIDADES_POR_DEFECTO = {
    "TUnit": "K",
    "PUnit": "MPa",
    "DUnit": "kg/m3",
    "HUnit": "kJ/mol",
    "WUnit": "m/s",
    "VisUnit": "uPa*s",
    "STUnit": "N/m",
}

UNIDADES_VALIDAS = {
    "TUnit": ("K", "ºC", "ºF", "R"),
    "PUnit": ("MPa", "bar", "atm", "torr", "psia"),
    "DUnit": ("kg/m3", "mol/l", "mol/m3", "g/l", "lb-mole/ft3", "lbm/ft3"),
    "HUnit": (
        "kJ/mol",
        "kJ/kg",
        "kcal/mol",
        "Btu/lb-mol",
        "kcal/g",
        "Btu/lbm",
    ),
    "WUnit": ("m/s", "ft/s", "mph"),
    "VisUnit": ("uPa*s", "Pa*s", "cP", "lbm/ft*s"),
    "STUnit": ("N/m", "dyn/cm", "lb/ft", "lb/in"),
}

ALIAS_BASE = {
    "T": ("Temperature", "Temperatura", "Temp"),
    "P": ("Pressure", "Presión", "Presion", "Pres"),
    "rho": ("Density", "Densidad"),
    "v": ("Volume", "Volumen", "Vol"),
    "u": ("Internal Energy", "Energía interna", "Energia interna"),
    "h": ("Enthalpy", "Entalpía", "Entalpia"),
    "s": ("Entropy", "Entropía", "Entropia"),
    "Cv": ("Cv",),
    "Cp": ("Cp",),
    "w": ("Sound Spd.", "Velocidad del sonido"),
    "JT": ("Joule-Thomson",),
    "mu": ("Viscosity", "Viscosidad"),
    "k": (
        "Therm. Cond.",
        "Conductividad térmica",
        "Conductividad termica",
        "Cond. térmica",
        "Cond. termica",
    ),
    "sig": ("Surf. Tension", "Tensión superficial", "Tension superficial"),
    "ph": ("Phase", "Fase"),
}

# Diccionario para definir el tipo de búsqueda, incorporando diferentes variantes
# que podría escribir el usuario. Como la búsqueda se hará sin tener en cuenta
# las mayúsculas usamos en cada clave `.casefold()`.
TIPOS_BUSQ_VALIDAS = {
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
    print("""
    'main' sin ningún efecto o implementación.\n
    Para visualizar algunos ejemplos, ver el cuaderno\n
    datos_nist_web_ejemplos.ipynb 
    """)

    return


# Función principal de búsqueda
def busqueda_web_nist(
    tipo_busq: str,
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
    tipo_busq: str
        Define el tipo de búsqueda. Formalmente puede ser:
          * "IsoBar"   (presión fija)
          * "IsoTherm" (temperatura fija)
          * "IsoChor"  (volumen fijo; se usa la densidad)
          * "SatP"     (Eq. líquido-vapor, presión a determinar —el rango dado
                        corresponde a la temperatura—)
          * "SatT"     (Eq. líquido-vapor, temperatura a determinar —el rango
                        dado corresponde a la presión—)
        Internamente se trabaja con alias para detectar otras formas esperables
        (por ejemplo, "T cte" e "Isotermico",  equivale a "IsoTherm"). Ver
        `datos_nist_web.TIPOS_BUSQ_VALIDAS`.

    iso_value : float o None
        Presión fija en las unidades seleccionadas (MPa por defecto), si
        tipo_busq="IsoBar". Temperatura fija en las unidades seleccionadas (K por
        defecto), si tipo_busq="IsoTherm". Densidad fija en las unidades
        seleccionadas (kg/m^3 por defecto), si tipo_busq="IsoChor". None o
        cualquier valor en caso contrario (no se utiliza).

    rg_min, rg_max, rg_interval: float
        Límites e intervalo de la variable que cambia, de acuerdo con la
        selección para `tipo_busq` y las unidades seleccionadas.

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
        Cualquier otro par clave-valor se ignora. Las unidades dadas deben ser
        válidas y respetar mayúsculas y minúsculas en este caso, para evitar
        ambigüedades. Para consultar el listado de unidades posibles y la forma
        en que deben ingresarse, vea:   `datos_nist_web.UNIDADES_VALIDAS`.

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
        tipo_busq,
        iso_value,
        rg_min,
        rg_max,
        rg_interval,
        decimales,
        sustancia,
        unidades,
    )

    try:
        consulta = requests.get(URL_BASE, params=parametros)
        consulta.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("La consulta web a", consulta.url, "falló con:")
        print("HTTP error:", e)
        print("No se pudo obtener la tabla de propiedades")

        return None

    return obtencion_datos(consulta, tipo_busq)


def obtencion_datos(consulta, tipo_busq):

    # Primero invertimos el diccionario de alias localmente:
    alias_inv = {
        nombre: key
        for key, nombres in ALIAS_BASE.items()
        for nombre in nombres
    }

    texto = consulta.text.splitlines()
    encabezados = texto[0]

    # 1. Separación de encabezados (general)
    encabezados = re.split(r"(?<=\))\s+", encabezados)
    # r"(?<=\))\s+" busca uno o más espacios en blanco,\s+, siempre que estén
    # precedidos por un paréntesis de cierre, \), donde la barra invertida es
    # para indicar un paréntesis literal.

    # 2. Expresión regular para interpretar los encabezados:
    patron_encabezado = re.compile(r"^(.*?)\s*(?:\((?:([lv]),\s*)?(.*?)\))?$")
    # La expresión `r"^(.*?)\s*(?:\((?:([lv]),\s*)?(.*?)\))?$"` permite separar
    # el encabezado en tres partes: el nombre de la variable, su fase y su
    # unidad. El primer grupo de captura, (.*?), identifica el nombre; el
    # segundo, ([lv]), identifica la fase ("l" o "v"); y el tercero, (.*?),
    # identifica la unidad.
    # Los grupos que comienzan con `?:` son grupos que no capturan información,
    # sino que permiten agrupar elementos de la expresión. En este caso,
    # permiten reconocer opcionalmente la fase y el bloque entre paréntesis.
    # Los paréntesis escapados, \( y \), representan paréntesis literales.
    # Finalmente, ^ y $ indican el inicio y el final del encabezado,
    # respectivamente. Los signos `?` indican que los elementos precedentes son
    # opcionales. Si un grupo de captura opcional no aparece en el encabezado,
    # su valor será `None` al recuperar los grupos mediante `.groups()`.

    if tipo_busq not in ["SatT", "SatP"]:
        # Una sola fase: reconstrucción directa de datos, encabezados y
        # unidades.

        encabezados_mod = []
        unidades = {}

        for encabezado in encabezados:
            nombre, _, unidad = patron_encabezado.match(encabezado).groups()

            variable = alias_inv.get(nombre, "¿" + nombre + "?")

            encabezados_mod.append(variable)
            unidades[variable] = unidad

        # Reconstrucción de datos como texto.
        datos = "\n".join(texto[1:])
        return PropData(
            datos,
            encabezados=encabezados_mod,
            unidades=unidades,
            alias_base=ALIAS_BASE,
        )

    # Si llegó hasta acá es porque fue una búsqueda en condiciones de
    # saturación. Tenemos que separar los datos leídos y devolver dos tablas.

    # 3. Clasificación e interpretación de columnas
    columnas = {"comunes": [], "l": [], "v": []}
    variables = []
    unidades = []

    for i, encabezado in enumerate(encabezados):
        nombre, fase, unidad = patron_encabezado.match(encabezado).groups()

        variable = alias_inv.get(nombre, "¿" + nombre + "?")

        variables.append(variable)
        unidades.append(unidad)

        grupo = fase if fase else "comunes"
        columnas[grupo].append(i)

    # 3. Construcción de índices, encabezados y unidades por fase
    indices_liq = columnas["comunes"] + columnas["l"]
    indices_vap = columnas["comunes"] + columnas["v"]

    encabezados_liq = [variables[i] for i in indices_liq] + ["ph"]
    encabezados_vap = [variables[i] for i in indices_vap] + ["ph"]

    unidades_liq = {variables[i]: unidades[i] for i in indices_liq}
    unidades_vap = {variables[i]: unidades[i] for i in indices_vap}

    unidades_liq["ph"] = None
    unidades_vap["ph"] = None

    # 4. Extracción de datos
    datos_liq = "\n".join(
        " ".join([*(linea.split()[i] for i in indices_liq), "liquid"])
        for linea in texto[1:]
    )

    datos_vap = "\n".join(
        " ".join([*(linea.split()[i] for i in indices_vap), "vapor"])
        for linea in texto[1:]
    )

    return (
        PropData(
            datos_liq,
            encabezados=encabezados_liq,
            unidades=unidades_liq,
            alias_base=ALIAS_BASE,
        ),
        PropData(
            datos_vap,
            encabezados=encabezados_vap,
            unidades=unidades_vap,
            alias_base=ALIAS_BASE,
        ),
    )


# Validación de datos y creación de links para buscar
# datos isobáricos o isotérmicos
def validar_entradas_y_crear_parametros(
    tipo_busq: str,
    iso_value: float | None,
    rg_min: float,
    rg_max: float,
    rg_interval: float,
    digitos: int,
    sustancia: Substance,
    unidades: dict[str, str],
) -> dict:

    # Determinación del valor adecuado de tipo_busq.
    tipo_busq = get_case_insensitive(tipo_busq)

    # Comprobación del valor de tipo_busq:
    if tipo_busq is None:
        raise ValueError("""
            'tipo_busq' debe ser compatible con:\n"
                * 'IsoBar'\n
                * 'IsoTherm'\n
                * 'IsoChor'\n
                * 'SatP'\n
                * 'SatT'\n
            """)

    # Comprobación sobre iso_value si corresponde:
    validar_numeros(iso_value, "iso_value", tipo_busq)

    # Comprobación sobre los restantes valores numéricos:
    validar_numeros(rg_min, "rg_min", None)
    validar_numeros(rg_max, "rg_max", None)
    validar_numeros(rg_interval, "rg_interval", None)

    # Validación de la cantidad de dígitos:
    digitos = validar_digitos(digitos)

    # Para las unidades no hacemos una validación estrictamente. Si están mal,
    # tomamos los valores por defecto.
    unidades_finales = validar_unidades(unidades)

    if not isinstance(sustancia, Substance):
        raise TypeError("`sustancia` debe pertenecer a la clase `Substance`.")

    parametros_variables = {
        "Type": tipo_busq,
        "Digits": digitos,
        "ID": sustancia.nist_id,
    }

    match tipo_busq:
        case "IsoBar":
            parametros_variables["P"] = iso_value
            parametros_variables["TLow"] = rg_min
            parametros_variables["THigh"] = rg_max
            parametros_variables["TInc"] = rg_interval

        case "IsoTherm":
            parametros_variables["T"] = iso_value
            parametros_variables["PLow"] = rg_min
            parametros_variables["PHigh"] = rg_max
            parametros_variables["PInc"] = rg_interval

        case "IsoChor":
            parametros_variables["D"] = iso_value
            parametros_variables["TLow"] = rg_min
            parametros_variables["THigh"] = rg_max
            parametros_variables["TInc"] = rg_interval

        case "SatP":
            parametros_variables["TLow"] = rg_min
            parametros_variables["THigh"] = rg_max
            parametros_variables["TInc"] = rg_interval

        case "SatT":
            parametros_variables["PLow"] = rg_min
            parametros_variables["PHigh"] = rg_max
            parametros_variables["PInc"] = rg_interval

    return {**PARAMETROS_FIJOS, **unidades_finales, **parametros_variables}


def validar_numeros(valor, nombre, tipo_busq):
    if nombre == "iso_value" and tipo_busq in ("SatP", "SatT"):
        # Puede ser None o cualquier otra cosa, el valor no se usará. No es
        # necesario continuar con la validación
        return

    if valor is None:
        if tipo_busq is None:  # valor no se trata de iso_value.
            raise ValueError(f"{nombre} es obligatorio")
        elif tipo_busq in {"IsoBar", "IsoTherm", "IsoChor"}:
            if nombre == "iso_value":
                raise ValueError(f"iso_value es obligatorio para {tipo_busq}")
            else:
                # En rigor, si llegó hasta acá, va a fallar en la próxima comprobación.
                # De todas maneras, dejamos la impresión del warning, porque puede
                # ser informativo.
                warnings.warn(
                    f"""
                    La combinación {valor = }, {nombre = } y {tipo_busq = }\n
                    sugiere un error en la entrada. Se continúa con las comprobaciones...
                    """
                )

    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"{nombre} debe ser un número.")

    try:
        if valor < 0 or not math.isfinite(valor):
            raise ValueError(
                f"{nombre} debe ser finito y mayor o igual que cero."
            )
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


def validar_unidades(unidades):
    if not isinstance(unidades, dict):
        return UNIDADES_POR_DEFECTO

    unidades_finales = UNIDADES_POR_DEFECTO.copy()
    for key, value in unidades.items():
        if key in unidades_finales and value in UNIDADES_VALIDAS[key]:
            unidades_finales[key] = value

    return unidades_finales


def get_case_insensitive(
    key: str,
) -> str | None:

    if key is None:
        return None

    if not isinstance(key, str):
        raise TypeError("Se esperaba un `str` o `None`.")

    return TIPOS_BUSQ_VALIDAS.get(key.casefold(), None)


if __name__ == "__main__":
    main()
