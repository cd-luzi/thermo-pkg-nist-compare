# Descripción
El proyecto busca comparar datos termodinámicos del agua como vapor sobrecalentado o en equilibrio líquido-vapor obtenidos de la página del NIST, frente a los datos calculados con el paquete "thermochem". Corresponde al proyecto final del curso [Python Científico](https://wpregliasco.github.io/python-sci/), del Instituto Balseiro.

<br>

# _De uso interno, para eliminar al terminar_


## Aspectos que tendríamos que cubrir
* Obtención de datos de la web del NIST (¿uso del paquete requests?) y generación de "tabla de datos" local
* Procesamiento de esos datos en forma de funciones para poder obtener y/o graficar datos isoentálpicos, isoentrópicos, etc.
* Uso y manejo del paquete thermochem para la generación del mismo juego de datos.
* Comparación y presentación

## Posibles librerías a emplear
### Generales
* numpy
* scipy?
* pandas (para la gestión de los datos como tablas y su visualización)
* matplotlib
* requests

### Vinculados a datos y funciones termodinámicas
* CoolProp (alternativa abierta más cercana a NIST REFPROP)
* iapws: Implementa exclusivamente los estándares de la International Association for the Properties of Water and Steam (IAPWS-95, IAPWS-IF97, etc.)
* thermochem

## Organización

Lectura de datos: leer de internet y bajarlos a un directorio o leerlos del directorio (en caso de que ya estén bajados los datos)

Interpolación de los datos: 
    -Se puede usar : np.interp (numpy), scipy.interpolate o DataFrame.interpolate (pandas)
    -obtener curvas para graficar, ej h vs P en curvas isotérmicas
    -tablas con algunas propiedades. Se debe poder elegir el rango, la cantidad de datos fija, como opción refinar el paso. 

Salidas finales: gráficos y las tablas. Decidir como guardarlas.

# Empezamos con esto, y vemos, si terminamos mucho antes, agregamos alguna otra cosa para hacer extra
