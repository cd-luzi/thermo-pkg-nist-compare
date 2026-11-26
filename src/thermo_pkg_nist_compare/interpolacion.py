from scipy.interpolate import make_interp_spline
import numpy as np


# incluye el valor en el fin
def interpolacion(x, y, comienzo=None, fin=None, espaciado=None):
    """
    Interpola un set de datos (x, y) con un spline cuadrático y lo evalúa en puntos equiespaciados.

    El spline es una función formada por polinomios de grado 2 pegados entre sí, que pasa por
    todos los puntos (x, y). Se evalúa desde comienzo cada espaciado, sin pasarse de fin pero
    incluyéndolo si cae justo en un paso. Para que el último punto no se pierda por errores de
    coma flotante, se le suma una tolerancia de 1e-9 al calcular la cantidad de pasos.
    Si comienzo y fin coinciden, se evalúa solo en ese punto.

    Fuera del rango de x el spline extrapola, así que esos valores pueden no ser confiables.

    Parámetros:
        x, y : array
            Datos a interpolar. Hacen falta al menos 3 puntos para el spline cuadrático.
        comienzo : float, opcional
            Valor de x donde empieza la evaluación. Por defecto, x[0].
        fin : float, opcional
            Valor de x donde termina la evaluación, incluido. Por defecto, x[-1].
        espaciado : float, opcional
            Paso entre los puntos de evaluación. Por defecto, (fin - comienzo) / 5.

    Devuelve:
        (puntos, valores) : tupla de arrays de numpy
            Los puntos de evaluación y los valores del spline en ellos.
    """

    if comienzo is None:
        comienzo = x[0]

    if fin is None:
        fin = x[-1]

    if fin == comienzo:
        # arma una función formada por polinomios de grado k pegados entre sí,
        # que pasa por todos los puntos.
        interp = make_interp_spline(x, y, 2)
        return interp(comienzo)

    if espaciado is None:
        espaciado = (fin - comienzo) / 5

    n = int(np.floor((fin - comienzo) / espaciado + 1e-9))
    # el 1e-9 evita perder el último punto por errores de coma flotante
    puntos = comienzo + espaciado * np.arange(n + 1)

    # arma una función formada por polinomios de grado k pegados entre sí, que
    # pasa por todos los puntos
    interp = make_interp_spline(x, y, 2)

    # Se evalúa la función en los puntos de interés y los retorna
    return (puntos, interp(puntos))
