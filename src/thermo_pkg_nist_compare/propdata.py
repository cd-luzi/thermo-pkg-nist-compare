from io import StringIO

import pandas as pd


# Esta breve clase es para evitar que `help PropData` agregue la extensa lista de información sobre pandas.
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
    un array de numpy cuando se pide por nombre.

    Además, permite acceder a las columnas mediante nombres alternativos
    definidos en el diccionario de alias de base (_ALIAS_BASE). Las columnas
    se almacenan utilizando abreviaturas, mientras que los alias permiten
    identificarlas mediante nombres alternativos (en inglés o español).

    Se puede acceder al diccionario de alias disponibles mediante:
        self.alias

    Para más información sobre los métodos heredados, consulta
    la documentación de pandas.DataFrame.
    """

    # Atributos personalizados que pandas conserva al crear copias o subconjuntos.
    # La tupla —("alias",)— evita usar una lista mutable —["alias"]— como atributo
    # de clase.
    _metadata = ("alias",)

    def __init__(self, datos=None, encabezados=None, alias_base=None):

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
            return

        if datos is None:
            super().__init__()
            self.alias = {}
            return

        if isinstance(datos, str):
            if datos.startswith(("http://", "https://")):
                raise NotImplementedError(
                    "Aún no se ha implementado la creación directa desde una URL.\n"
                    "Usar `busqueda_web_nist` en su lugar, si lo que se quiere es leer datos desde la web del NIST"
                )
            elif "\n" in datos or "\t" in datos or "," in datos:
                # StringIO hace que pandas reciba el texto de la misma forma que
                # si estuviera leyendo un archivo.
                fuente = StringIO(datos)
            else:
                fuente = datos  # Ruta de archivo
        else:
            fuente = datos  # Archivo abierto o objeto compatible

        super().__init__(
            pd.read_csv(
                fuente,
                sep=r"\s+",
                names=encabezados,
                dtype={"Phase": str},
                engine="python",
            )
        )

        self._generate_aliases(self.columns, alias_base)

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
        # Esto es para que los alias solo estén asociados a la tabla actual cuando la misma se reduce
        result = super().__finalize__(other, method=method, **kwargs)
        if hasattr(self, "alias"):
            self.alias = {
                alias: columna
                for alias, columna in self.alias.items()
                if columna in self.columns
            }
        return result

    def _generate_aliases(self, encabezados, alias_base):

        if alias_base is None:
            self.alias = {}
            return

        aliases = {}

        for clave, nombres in alias_base.items():
            if clave in encabezados:
                for nombre in nombres:
                    aliases[nombre] = clave

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
    print("Clase básica para generar tablas de propiedades basadas en pandas.")


if __name__ == "__main__":
    main()
