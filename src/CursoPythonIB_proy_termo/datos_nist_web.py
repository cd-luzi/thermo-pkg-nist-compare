import json
import requests


"""
"""

def main():
    TODO


# Función principal de búsqueda
def busqueda_web():
    TODO


# Creación de links para buscar datos isobáricos
# a una única presión, barriendo la temperatura
def crear_link_isobar(
        p_val: float,
        T_high: float,
        T_low: float,
        delta_T: float,
        ) -> str:
    
    return (
        "https://webbook.nist.gov/cgi/fluid.cgi?"
        f"Action=Data&Wide=on&ID=C7732185&Type=IsoBar"
        f"&Digits=12&P={p_val}&TLow={T_low}&THigh={T_high}&TInc={delta_T}"
        r"&RefState=DEF&TUnit=K&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fmol"
        r"&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm"
        )


# Creación de links para buscar datos isotérmicos
# a una única temperatura, barriendo la presión
def crear_link_isoterm(
        T_val: float,
        p_high: float,
        p_low: float,
        delta_p: float,
        ) -> str:
    
    return (
        "https://webbook.nist.gov/cgi/fluid.cgi?"
        f"Action=Data&Wide=on&ID=C7732185&Type=IsoBar"
        f"&Digits=12&T={T_val}&PLow={p_low}&PHigh={p_high}&PInc={delta_p}"
        r"&RefState=DEF&TUnit=K&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fmol"
        r"&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm"
        )


if __name__ == "__main__":
    main()
