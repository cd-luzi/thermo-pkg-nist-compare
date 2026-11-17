'''
Interpolación de los datos: 
    -Se puede usar : make_interp_spline(x, y, k=3, t=None, bc_type=None, axis=0, check_finite=True)[source]
    -obtener curvas para graficar, ej h vs P en curvas isotérmicas
    -tablas con algunas propiedades. Se debe poder elegir el rango, la cantidad de datos fija, como opción refinar el paso. 
    -Salidas finales: gráficos y las tablas. Decidir como guardarlas.
'''

from scipy.interpolate import make_interp_spline
import numpy as np

def interpolacion(x, y, comienzo=None, fin=None, espaciado=None): # incluye el valor en el fin

    if fin==comienzo: 
        interp = make_interp_spline(x, y, 2) # arma una función formada por polinomios de grado k pegados entre sí, que pasa por todos los puntos 
        return (interp(comienzo)) 
        
    if comienzo==None:
        comienzo = x[0]

    if fin==None:
        fin = x[-1]

    if espaciado==None:
        espaciado = ((fin-comienzo)/5)

    cantidad = round((fin - comienzo) /  espaciado) + 1
    puntos = np.linspace(comienzo, fin, cantidad)
    interp = make_interp_spline(x, y, 2) # arma una función formada por polinomios de grado k pegados entre sí, que pasa por todos los puntos
    
    return (puntos, interp(puntos)) # aca se evalua la funcion en los puntos de interés y los retorna


# parametros para probar, los pueden descomentar y cambiar cosas si quieren

#x = np.array([0, 1, 2, 3, 4])
#y = np.array([0, 0.8, 0.9, 0.1, -0.8])

#tabla_interpolada = interpolacion(x, y, 0, 4, 1) 

#print(tabla_interpolada)