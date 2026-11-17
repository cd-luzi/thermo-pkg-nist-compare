'''
Interpolación de los datos: 
    -obtener curvas para graficar, ej h vs P en curvas isotérmicas
    -Salidas finales: gráficos y las tablas. Decidir como guardarlas.
'''

from scipy.interpolate import make_interp_spline
import numpy as np

def interpolacion(x, y, comienzo=None, fin=None, espaciado=None): # incluye el valor en el fin
        
    if comienzo==None:
        comienzo = x[0]

    if fin==None:
        fin = x[-1]
        
    if fin==comienzo: 
            interp = make_interp_spline(x, y, 2) # arma una función formada por polinomios de grado k pegados entre sí, que pasa por todos los puntos 
            return (interp(comienzo)) 

    if espaciado==None:
        espaciado = ((fin-comienzo)/5)

    cantidad = round((fin - comienzo) /  espaciado) + 1
    puntos = np.linspace(comienzo, fin, cantidad)
    interp = make_interp_spline(x, y, 2) # arma una función formada por polinomios de grado k pegados entre sí, que pasa por todos los puntos
    
    return (puntos, interp(puntos)) # aca se evalua la funcion en los puntos de interés y los retorna


