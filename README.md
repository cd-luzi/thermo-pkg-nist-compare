# Thermo_pkg_nist_compare

## Descripción
Proyecto que facilita la comparación de datos termodinámicos de diferentes sustancias disponibles en forma gratuita en la [web del NIST](https://webbook.nist.gov/chemistry/fluid/), limitados a condición supercrítica, vapor sobrecalentado o equilibrio líquido-vapor, frente a los datos calculados con el paquete [CoolProp](https://coolprop.org/) de Python. Si la sustancia elegida es el agua, este último permite elegir entre dos tipos de variantes (IAPWS95 y IAPWS-97).

Este paquete corresponde al proyecto final del curso [Python Científico](https://wpregliasco.github.io/python-sci/), del [Instituto Balseiro](https://www.ib.edu.ar/).

### Autores
* Jazmín Luminari - https://github.com/jazminluminari
* Carolina Cogo - https://github.com/caro-88
* Carlos Luzi - https://github.com/cd-luzi

## Destacados
* Propiedades termodinámicas desde el WebBook del NIST, con construcción automatizada del link de búsqueda.
* Ejemplos de aplicación del paquete CoolProp.
* Exportación automática de gráficos comparativos, con interpolación para el suavizado de curvas.
* Propiedades como tablas de Pandas modificada, para facil acceso e impresión en pantalla.

## Instalación
Se sugiere instalarlo empleando `uv`.

Desde una carpeta local:

```bash
uv add ../thermo-pkg-nist-compare
```

Desde el repositorio de github:
```bash
uv add git+https://github.com/cd-luzi/thermo-pkg-nist-compare
```

Clonando el repositorio con:
```bash
git clone https://github.com/cd-luzi/thermo-pkg-nist-compare.git
```

### Verificación rápida del paquete:
Se sugiere correr todos los ejemplos 1 a 4: con `uv run ./examples/ejemplo0x.py`, donde x es un número de 1 a 4, y verificar que no haya errores. Los ejemplos son:
* [Ejemplo 01](examples/ejemplo01.py)
* [Ejemplo 02](examples/ejemplo02.py)
* [Ejemplo 03](examples/ejemplo03.py)
* [Ejemplo 04](examples/ejemplo04.py)


## Modo de empleo

### Elección de sustancia (web) y búsqueda web

_**Ejemplo básico**_:
```python
>>> from thermo_pkg_nist_compare.datos_web_nist import busqueda_web_nist
>>> from thermo_pkg_nist_compare.substancelist import Substance
>>> s = Substance.from_alias("benceno")
>>> data_table = busqueda_web_nist(
>>>     tipo_busq="IsoTherm",
>>>     iso_value=383,
>>>     rg_min=0.5,
>>>     rg_max=15,
>>>     rg_interval=0.5,
>>>     unidades = {
>>>         "PUnit": "bar",
>>>         "HUnit": "kJ/kg",
>>>         },
>>>     sustancia = sust,
>>> )

```


_**Ejemplos detallados en:**_:
* [datos_nist_web_ejeplos_y_uso](examples/datos_nist_web_ejemplos_y_uso.ipynb)
* [propdata_ejemplos_y_uso](examples/propdata_ejemplos_y_uso.ipynb)

<br>


### Graficadora y otras aplicaciones

_**Ejemplo básico**_:
```py
>>> from thermo_pkg_nist_compare.graficadora import graficar
>>> import numpy as np
>>> x = np.array([0, 1, 2, 3, 4])
>>> y = np.array([0, 0.8, 0.9, 0.1, -0.8])
>>> graficar(x, y, nombre_x="temperatura", nombre_y="presion", unidad_x="°C", unidad_y="Pa")
```

**Ejemplos detallados en:**_:
* [graficadora_ejemplos_y_uso](examples/graficadora_ejemplos_y_uso.ipynb)
* [generador_tablas_ejemplos_y_uso](examples/generador_tablas_ejemplos_y_uso.ipynb)
* [interpolacion_ejemplos_y_uso](examples/interpolacion_ejemplos_y_uso.ipynb)

<br>

### Uso de CoolProp
Para consultar todas las capacidades del paquete, se sugiere consultar la web oficial: [CoolProp](https://coolprop.org/).

Para visualizar ejemplos más sencillos de interés para este paquete, ver los ejemplos específicos desarrollados a tal fin:
* [coolprop_ejemplos_y_uso](examples/coolprop_ejemplos_y_uso.ipynb)

### Otros paquetes termodinámicos
Se dispone de un ejemplo básico analizando otros paquetes en:
* [pkg_existentes_ejemplos_y_uso](examples/pkg_existentes_ejemplos_y_uso.ipynb)


### Ejemplo completo de uso y comparación
Puede consultar un ejemplo completo que involucra la consulta web y evaluación mediante CoolProp de propiedades del agua, así como la creación de diferentes gráficos comparativos, en:
* [ejemplo_principal01](examples/ejemplo_principal01.ipynb)

<br>

## Contribuciones y comentarios
Si tiene algún comentario, puede contactarnos en forma directa o crear un `issue` o un `pull request` según sea necesario.