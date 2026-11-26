from io import StringIO

import numpy as np
import pandas as pd


# Esta breve clase es para evitar que `help PropData` agregue la extensa lista
# de información sobre pandas.
class _PropDataHelpMeta(type):
    def __dir__(cls):
        local = set(cls.__dict__)
        inherited = set()

        for base in cls.__mro__[1:]:
            inherited.update(base.__dict__)

        inherited.difference_update(local)
        return sorted(set(type.__dir__(cls)) - inherited)


class PropData(pd.DataFrame, metaclass=_PropDataHelpMeta):
    """
    Clase básica que hereda todo de DataFrame de pandas, pero que
    modifica el método __getitem__ para que devuelva directamente
    un array de numpy cuando se pide una sola columna por nombre.

    La creación de la tabla de propiedades puede hacerse desde un
    `str` proveniente de un archivo o web ya procesado, desde una
    lista de listas, desde un nparray de numpy, desde una ruta de
    archivo a leer o desde un archivo abierto o un objeto compatible
    con pd.read_csv().

    Se debe tener en cuenta que no se realizan comprobaciones de
    compatibilidad entre la lista de encabezados (que puede ser None)
    y los datos. Se asume que ya se aseguró por fuera que la
    cantidad de datos y nombres sea coherente.

    Además, permite acceder a las columnas mediante nombres alternativos
    definidos en el diccionario de alias de base (alias_base) si se
    proporciona. Las columnas se almacenan utilizando abreviaturas,
    mientras que los alias permiten identificarlas mediante nombres
    alternativos (en inglés o español).

    Se puede acceder al diccionario de alias generado desde alias_base
    mediante:
        self.alias

    Para más información sobre los métodos heredados, consulta
    la documentación de pandas.DataFrame.
    """

    # Atributos personalizados que pandas conserva al crear copias o
    # subconjuntos. La tupla —("alias",)— evita usar una lista mutable
    # —["alias"]— como atributo de clase.
    _metadata = ("alias", "unidades", "_catalogo_alias")

    def __init__(
        self, datos=None, encabezados=None, unidades=None, alias_base=None
    ):

        if datos is None:
            super().__init__()
            self.alias = {}
            self.unidades = {}
            self._catalogo_alias = {}
            return

        if isinstance(datos, pd.DataFrame):
            super().__init__(datos)
            if alias_base is not None:
                self._generate_aliases(self.columns, alias_base)
            else:
                aliases = getattr(datos, "alias", {})
                self.alias = {
                    alias: columna
                    for alias, columna in aliases.items()
                    if columna in self.columns
                }

                catalogo_alias = getattr(datos, "_catalogo_alias", None)
                if catalogo_alias is None:
                    catalogo_alias = aliases
                self._catalogo_alias = dict(catalogo_alias)

            if unidades is not None:
                self.unidades = unidades
            else:
                undds = getattr(datos, "unidades", {})
                self.unidades = {
                    var: unidad
                    for var, unidad in undds.items()
                    if var in self.columns
                }

            return

        if isinstance(datos, np.ndarray):
            super().__init__(pd.DataFrame(datos, columns=encabezados))
            self._generate_aliases(self.columns, alias_base)
            self.unidades = unidades
            return

        if isinstance(datos, list):
            num_filas = len(datos)
            num_cols = len(datos[0])

            if not all(len(fila) == num_cols for fila in datos):
                raise TypeError("La lista proporcionada es incompatible.")

            if num_cols == len(encabezados):
                # Ya está preparada como corresponde.
                pass
            elif num_filas == len(encabezados):
                # Hay que "trasponer" la lista
                datos = [list(columna) for columna in zip(*datos)]
            else:
                raise TypeError("La lista proporcionada es incompatible.")

            super().__init__(pd.DataFrame(datos, columns=encabezados))
            self._generate_aliases(self.columns, alias_base)
            self.unidades = unidades
            return

        if isinstance(datos, str):
            if datos.startswith(("http://", "https://")):
                raise NotImplementedError(
                    "Aún no se ha implementado la creación "
                    "directa desde una URL.\n"
                    "Usar `busqueda_web_nist` en su lugar, si lo que "
                    "se quiere es leer datos desde la web del NIST"
                )
            elif "\n" in datos or "\t" in datos or "," in datos:
                # StringIO hace que pandas reciba el texto de la misma forma
                # que si estuviera leyendo un archivo.
                fuente = StringIO(datos)
            else:
                fuente = datos  # Ruta de archivo
        else:
            fuente = datos  # ¿Archivo abierto o objeto compatible?

        try:
            super().__init__(
                pd.read_csv(
                    fuente,
                    sep=r"\s+",
                    names=encabezados,
                    dtype={"Phase": str},
                    engine="python",
                )
            )
        except (TypeError, ValueError) as e:
            raise TypeError(
                "Los datos proporcionados no tienen un formato compatible."
            ) from e

        self._generate_aliases(self.columns, alias_base)
        self.unidades = unidades

        return

    def __str__(self):

        unidades = getattr(self, "unidades", {})

        tabla = pd.DataFrame(self)

        tabla.columns = pd.MultiIndex.from_arrays(
            [
                tabla.columns,
                [unidades.get(columna) or "" for columna in tabla.columns],
            ]
        )

        return tabla.to_string(justify="center")

    __repr__ = __str__

    @property
    def _constructor(self):
        """
        Con esto nos garantizamos que las operaciones que devolverían un
        DataFrame de pandas nos sigan devolviendo la clase así definida. De
        esta manera, si data_table es una tabla creada con PropData, la
        operación data_table[["T", "P"]] devolverá una clase PropData en
        lugar de un DataFrame puro.
        """
        return PropData

    def __finalize__(self, other, method=None, **kwargs):
        # Esto es para que los alias solo estén asociados a la tabla actual
        # cuando la misma se reduce.
        result = super().__finalize__(other, method=method, **kwargs)

        if hasattr(self, "alias"):
            self.alias = {
                alias: columna
                for alias, columna in self.alias.items()
                if columna in self.columns
            }

        if hasattr(self, "unidades"):
            self.unidades = {
                columna: unidad
                for columna, unidad in self.unidades.items()
                if columna in self.columns
            }

        return result

    def _generate_aliases(self, encabezados, alias_base):

        if alias_base is None:
            self._catalogo_alias = {}
            self.alias = {}
            return

        catalogo = {
            nombre: clave
            for clave, nombres in alias_base.items()
            for nombre in nombres
        }

        self._catalogo_alias = catalogo
        self.alias = {
            nombre: clave
            for nombre, clave in catalogo.items()
            if clave in encabezados
        }

    def __getitem__(self, keys):

        if isinstance(keys, list):
            keys = [
                self.alias.get(k, k) if isinstance(k, str) else k for k in keys
            ]

        if isinstance(keys, str):
            keys = self.alias.get(keys, keys)

        result = super().__getitem__(keys)

        if isinstance(result, pd.Series):
            return result.to_numpy()

        return result

    def __setitem__(self, key, value):
        if isinstance(key, str):
            key = self._catalogo_alias.get(key, key)
        elif isinstance(key, list):
            key = [
                self._catalogo_alias.get(k, k) if isinstance(k, str) else k
                for k in key
            ]

        super().__setitem__(key, value)

        self.alias.update(
            {
                alias: columna
                for alias, columna in self._catalogo_alias.items()
                if columna in self.columns
            }
        )


def main() -> None:
    print("Clase básica para generar tablas de propiedades basadas en pandas.")


if __name__ == "__main__":
    main()
