from enum import Enum, EnumMeta


class SubstanceEnumMeta(EnumMeta):
    """
    MetaClase usada para imprimir información a nivel clase y no objeto. Se usa
    para que el usuario pueda consultar el listado de sustancias disponibles y
    se imprima de forma ordenada y prolija, omitiendo información que no sería
    de su interés (el ID).
    """

    def __str__(cls):
        headers = ("Nombre (Esp.)", "Nombre (Eng.)", "Fórmula")

        rows = [
            (nombre_es, nombre_en, formula)
            for formula, nombre_es, nombre_en in (member.value for member in cls)
        ]

        widths = [
            max(len(header), *(len(row[i]) for row in rows))
            for i, header in enumerate(headers)
        ]

        header = " | ".join(f"{name:<{width}}" for name, width in zip(headers, widths))

        separator = "-+-".join("-" * width for width in widths)

        body = [
            " | ".join(f"{value:<{width}}" for value, width in zip(row, widths))
            for row in rows
        ]

        return (
            "Las sustancias disponibles son:\n\n"
            + header
            + "\n"
            + separator
            + "\n"
            + "\n".join(body)
        )


class Substance(Enum, metaclass=SubstanceEnumMeta):
    """
    Clase basada enb "Enum". Contiene el listado de las sustancias disponibles
    en el webbook del NIST (abierto) con la fórmula, el nombre en inglés y en
    español como valores (como tupla) y el ID como nombre. Incorpora un método
    (`from_alias`) que permite crear el objeto desde alguno de los valores
    (se recomienda esa forma de uso). Por ejemplo, las siguientes formas son
    todas equivalentes:
    ´´´Python
    sust = Substance.from_alias("agua")
    sust = Substance.from_alias("water")
    sust = Substance.from_alias("H2O")
    ´´´

    Si en `busqeuda_web_nist` se quiere usar una sustancia diferente al agua,
    se debe llamar primero a esta clase (por ejemplo, `sust = Substance("H2")`)
    y luego pasar sust como valor del argumento `sustancia` en `busqeuda_web_nist`.
    Internamente, esa función leerá el ID para el NIST desde sust.nist_id.
    Para ver el listado de sustancias disponibles, ejecutar:
    `print(Substance)`
    """

    # ID = (formula, nombre_español, nombre_ingles)

    C7732185 = ("H2O", "Agua", "Water")
    C7727379 = ("N2", "Nitrógeno", "Nitrogen")
    C1333740 = ("H2", "Hidrógeno", "Hydrogen")
    B5000001 = ("H2", "Parahidrógeno", "Parahydrogen")
    C7782390 = ("D2", "Deuterio", "Deuterium")
    C7782447 = ("O2", "Oxígeno", "Oxygen")
    C7782414 = ("F2", "Flúor", "Fluorine")
    C630080 = ("CO", "Monóxido de carbono", "Carbon monoxide")
    C124389 = ("CO2", "Dióxido de carbono", "Carbon dioxide")
    C10024972 = ("N2O", "Óxido nitroso", "Dinitrogen monoxide")
    C7789200 = ("D2O", "Agua pesada", "Deuterium oxide")

    C67561 = ("CH4O", "Metanol", "Methanol")
    C74828 = ("CH4", "Metano", "Methane")
    C74840 = ("C2H6", "Etano", "Ethane")
    C74851 = ("C2H4", "Etileno", "Ethene")
    C74986 = ("C3H8", "Propano", "Propane")
    C115071 = ("C3H6", "Propileno", "Propene")
    C74997 = ("C3H4", "Propino", "Propyne")
    C75194 = ("C3H6", "Ciclopropano", "Cyclopropane")
    C106978 = ("C4H10", "Butano", "Butane")
    C75285 = ("C4H10", "Isobutano", "Isobutane")
    C109660 = ("C5H12", "Pentano", "Pentane")
    C78784 = ("C5H12", "2-Metilbutano", "2-Methylbutane")
    C463821 = ("C5H12", "Neopentano", "2,2-Dimethylpropane")
    C110543 = ("C6H14", "Hexano", "Hexane")
    C107835 = ("C6H14", "2-Metilpentano", "2-Methylpentane")
    C110827 = ("C6H12", "Ciclohexano", "Cyclohexane")
    C142825 = ("C7H16", "Heptano", "Heptane")
    C111659 = ("C8H18", "Octano", "Octane")
    C111842 = ("C9H20", "Nonano", "Nonane")
    C124185 = ("C10H22", "Decano", "Decane")
    C112403 = ("C12H26", "Dodecano", "Dodecane")

    C7440597 = ("He", "Helio", "Helium")
    C7440019 = ("Ne", "Neón", "Neon")
    C7440371 = ("Ar", "Argón", "Argon")
    C7439909 = ("Kr", "Criptón", "Krypton")
    C7440633 = ("Xe", "Xenón", "Xenon")

    C7664417 = ("NH3", "Amoníaco", "Ammonia")
    C7783542 = ("NF3", "Trifluoruro de nitrógeno", "Nitrogen trifluoride")

    C75694 = ("CCl3F", "Triclorofluorometano", "Trichlorofluoromethane")
    C75718 = ("CCl2F2", "Diclorodifluorometano", "Dichlorodifluoromethane")
    C75729 = ("CClF3", "Clorotrifluorometano", "Chlorotrifluoromethane")
    C75730 = ("CF4", "Tetrafluorometano", "Tetrafluoromethane")
    C75434 = ("CHCl2F", "Diclorofluorometano", "Dichlorofluoromethane")
    C75456 = ("CHClF2", "Clorodifluorometano", "Chlorodifluoromethane")
    C75467 = ("CHF3", "Trifluorometano", "Trifluoromethane")
    C75105 = ("CH2F2", "Difluorometano", "Difluoromethane")
    C593533 = ("CH3F", "Fluorometano", "Fluoromethane")

    C76131 = (
        "C2Cl3F3",
        "1,1,2-Tricloro-1,2,2-trifluoroetano",
        "1,1,2-Trichloro-1,2,2-trifluoroethane",
    )
    C76142 = (
        "C2Cl2F4",
        "1,2-Dicloro-1,1,2,2-tetrafluoroetano",
        "1,2-Dichloro-1,1,2,2-tetrafluoroethane",
    )
    C76153 = ("C2ClF5", "Cloropentafluoroetano", "Chloropentafluoroethane")
    C76164 = ("C2F6", "Hexafluoroetano", "Hexafluoroethane")
    C306832 = (
        "C2HCl2F3",
        "2,2-Dicloro-1,1,1-trifluoroetano",
        "2,2-Dichloro-1,1,1-trifluoroethane",
    )
    C2837890 = (
        "C2HClF4",
        "1-Cloro-1,2,2,2-tetrafluoroetano",
        "1-Chloro-1,2,2,2-tetrafluoroethane",
    )
    C354336 = ("C2HF5", "Pentafluoroetano", "Pentafluoroethane")
    C811972 = ("C2H2F4", "1,1,1,2-Tetrafluoroetano", "1,1,1,2-Tetrafluoroethane")
    C1717006 = ("C2H3Cl2F", "1,1-Dicloro-1-fluoroetano", "1,1-Dichloro-1-fluoroethane")
    C75683 = ("C2H3ClF2", "1-Cloro-1,1-difluoroetano", "1-Chloro-1,1-difluoroethane")
    C420462 = ("C2H3F3", "1,1,1-Trifluoroetano", "1,1,1-Trifluoroethane")
    C75376 = ("C2H4F2", "1,1-Difluoroetano", "1,1-Difluoroethane")

    C76197 = ("C3F8", "Octafluoropropano", "Octafluoropropane")
    C431890 = (
        "C3H1F7",
        "1,1,1,2,3,3,3-Heptafluoropropano",
        "1,1,1,2,3,3,3-Heptafluoropropane",
    )
    C431630 = (
        "C3H2F6",
        "1,1,1,2,3,3-Hexafluoropropano",
        "1,1,1,2,3,3-Hexafluoropropane",
    )
    C690391 = (
        "C3H2F6",
        "1,1,1,3,3,3-Hexafluoropropano",
        "1,1,1,3,3,3-Hexafluoropropane",
    )
    C679867 = ("C3H3F5", "1,1,2,2,3-Pentafluoropropano", "1,1,2,2,3-Pentafluoropropane")
    C460731 = ("C3H3F5", "1,1,1,3,3-Pentafluoropropano", "1,1,1,3,3-Pentafluoropropane")
    C115253 = ("C4F8", "Octafluorociclobutano", "Octafluorocyclobutane")

    C71432 = ("C6H6", "Benceno", "Benzene")
    C108883 = ("C7H8", "Tolueno", "Toluene")
    C355259 = ("C4F10", "Decafluorobutano", "Decafluorobutane")
    C678262 = ("C5F12", "Dodecafluoropentano", "Dodecafluoropentane")

    C7446095 = ("SO2", "Dióxido de azufre", "Sulfur dioxide")
    C7783064 = ("H2S", "Sulfuro de hidrógeno", "Hydrogen sulfide")
    C2551624 = ("SF6", "Hexafluoruro de azufre", "Sulfur hexafluoride")
    C463581 = ("COS", "Sulfuro de carbonilo", "Carbonyl sulfide")

    @property
    def nist_id(self):
        return self.name

    @property
    def formula(self):
        return self.value[0]

    @property
    def spanish(self):
        return self.value[1]

    @property
    def english(self):
        return self.value[2]

    @classmethod
    def from_alias(cls, alias):
        alias = alias.casefold()

        return next(
            (
                substance
                for substance in cls
                if alias in (s.casefold() for s in substance.value)
            ),
            None,
        )

    def __str__(self):
        formula, nombre_es, nombre_en = self.value

        return (
            f"La sustancia elegida es '{nombre_es}'.\n"
            "Alias adicionales:\n"
            f" * '{nombre_en}'\n"
            f" * '{formula}'\n"
            "NIST ID:\n"
            f" * '{self.name}'"
        )


def main() -> None:
    print(
        "Clase basada en Enum que contiene el listado de sustancias\n"
        "disponibles en forma abierta en el NIST."
    )


if __name__ == "__main__":
    main()
