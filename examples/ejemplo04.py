# Para hacer:
# Volcar un ejemplo básico de uso y testeo de los paquetes termodinámicos
# (llamándolos en forma directa o por otro programa creado). La idea es que
# sirva para el testeo rápido desde la línea de comandos de alguien
# que descargue el proyecto.

import CoolProp.CoolProp as CP
from CoolProp.CoolProp import PhaseSI
from thermo_pkg_nist_compare.propdata import PropData
import numpy as np

model_disp={"IAPWS95":"Water","IAPWS-97":"IF97::Water"}

modelo = input("Ingrese el modelo a usar (IAPWS95 o IAPWS-97): ")

#modelo = "IAPWS-97"  # Para pruebas rápidas, se puede cambiar a "IAPWS-97"

if modelo not in model_disp:
    raise ValueError("Modelo no válido. Debe ser 'IAPWS95' o 'IAPWS-97'.")

P = np.linspace(1e4,1e5,10)/1000    # kPa

T = np.linspace(300,400,10)    # K

u = CP.PropsSI("Umass", "P", P*1000, "T", T, model_disp[modelo])/1000 # kJ/(kg K)
h = CP.PropsSI("Hmass", "P", P*1000, "T", T, model_disp[modelo])/1000  # kJ/kg
s = CP.PropsSI("Dmass", "P", P*1000, "T", T, model_disp[modelo])/1000 # kJ/kg
    
encabezados = ["T", "P", "u", "h", "s"]

unidades = {"T": "K", "P": "kPa", "u": "kJ/kg", "h" : "kJ/kg", "s":"kJ/kg*K"}

tabla_array = np.column_stack((T, P, u, h, s))

tabla = PropData(datos=tabla_array, encabezados=encabezados, unidades=unidades)

print(tabla)

fases = [
    PhaseSI("P", float(p) * 1000, "T", float(t), model_disp[modelo])
    for p, t in zip(P, T)
]

tabla["fase"] = fases

tabla.unidades["fase"] = ""

print(tabla)