from thermo_pkg_nist_compare import busqueda_web_nist
from thermo_pkg_nist_compare import Substance


def main() -> None:
    print("""
    Buscando la curva de equilibrio líquido-vapor para el agua en
    la web del NIST:
    """)

    try:
        sustancia = Substance.from_alias("agua")

        tabla_liq_agua, tabla_vap_agua = busqueda_web_nist(
            tipo_busq="SatT",
            iso_value=None,
            rg_min=0.01,
            rg_max=5.01,
            rg_interval=0.1,
            unidades={"PUnit": "bar"},
            sustancia=sustancia,
        )

        print(tabla_liq_agua[["T", "P", "u", "h", "s", "ph"]])
        print("\n", tabla_vap_agua[["T", "P", "u", "h", "s", "ph"]], "\n")

    except Exception as e:
        raise Exception("""
        Algo falló. Revisar la instalación o contactarse con
        los desarroladores.
        """) from e


if __name__ == "__main__":
    main()
