# Thermo_pkg_nist_compare

## Destacados
* Busqueda de propiedades termodinámicas en el WebBook del NIST.
* Estimación de propiedades termodinámicas mediante CoolProp.
* Gráficos comparativos, interpolación y salidas en forma de tablas.

## Descripción
Proyecto que facilita la comparación de datos termodinámicos de diferentes sustancias disponibles en forma gratuita en la [web del NIST](https://webbook.nist.gov/chemistry/fluid/), limitados a condición supercrítica, vapor sobrecalentado o equilibrio líquido-vapor, frente a los datos calculados con el paquete [CoolProp](https://coolprop.org/) de Python. Si la sustancia elegida es el agua, este último permite elegir entre dos tipos de variantes (IAPWS95 y IAPWS-97).

Este paquete corresponde al proyecto final del curso [Python Científico](https://wpregliasco.github.io/python-sci/), del [Instituto Balseiro](https://www.ib.edu.ar/).

### Autores
* Jazmín Luminari - https://github.com/jazminluminari
* Carolina Cogo - https://github.com/caro-88
* Carlos Luzi - https://github.com/cd-luzi

## Modo de empleo
Elección de sustancia (web) y búsqueda web:
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

Graficadora de datos, con posibilidad de pasar por separado nombres y unidades.

```py
>>> from thermo_pkg_nist_compare.graficadora import graficar
>>> import numpy as np
>>> x = np.array([0, 1, 2, 3, 4])
>>> y = np.array([0, 0.8, 0.9, 0.1, -0.8])
>>> graficar(x, y, nombre_x="temperatura", nombre_y="presion", unidad_x="°C", unidad_y="Pa")
```

Uso de CoolProp: se sufiere consultar la web oficial: [CoolProp](https://coolprop.org/)

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

## Contribuciones y comentarios
