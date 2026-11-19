from scipy.interpolate import make_interp_spline
import numpy as np

def interpolacion(x, y, comienzo=None, fin=None, espaciado=None): # incluye el valor en el fin
    """
    Interpola (x, y) con un spline cuadrático y lo evalúa en puntos equiespaciados.

    Evalúa desde `comienzo` cada `espaciado`, sin pasarse de `fin`, pero incluyéndolo.
    Por defecto: comienzo=x[0], fin=x[-1], espaciado=(fin-comienzo)/5.
    Fuera del rango de `x` extrapola, así que esos valores pueden no ser confiables.

    Devuelve (puntos, valores) como arrays de numpy.
    """
        
    if comienzo==None:
        comienzo = x[0]

    if fin==None:
        fin = x[-1]
        
    if fin==comienzo: 
            interp = make_interp_spline(x, y, 2) # arma una función formada por polinomios de grado k pegados entre sí, que pasa por todos los puntos 
            return (interp(comienzo)) 

    if espaciado==None:
        espaciado = ((fin-comienzo)/5)

    n = int(np.floor((fin - comienzo) / espaciado + 1e-9))  # el 1e-9 evita perder el último punto por errores de coma flotante
    puntos = comienzo + espaciado * np.arange(n + 1)
    interp = make_interp_spline(x, y, 2) # arma una función formada por polinomios de grado k pegados entre sí, que pasa por todos los puntos
    
    return (puntos, interp(puntos)) # aca se evalua la funcion en los puntos de interés y los retorna


