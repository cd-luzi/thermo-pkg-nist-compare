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
Deberíamos dividir las tareas de acuerdo con los Aspectos a cubrir. Modifiquen y propongan a gusto.