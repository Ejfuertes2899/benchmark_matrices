# Ficha FAIR de los datos del experimento

## Qué contienen los datos

Se midió el tiempo de multiplicación de matrices en C++, Go, Java y Python.
Se usaron tres tamaños de matriz, 500, 1000 y 1500, con 10 repeticiones
por combinación de lenguaje y tamaño. El conjunto contiene 120 mediciones.
Las ejecuciones de calentamiento quedaron fuera de los CSV.

## Procedencia

Las mediciones se obtuvieron al ejecutar las cuatro implementaciones en
contenedores Docker, coordinados mediante Snakemake. Cada lenguaje usó
las mismas matrices para cada tamaño. Las matrices de entrada y su
manifiesto se incluyen en `03_crear matrices/`.

El archivo [orden.csv](05_resultados/orden.csv) registra el orden del
experimento. Los [registros del equipo](02_caracteristicas_equipo/)
documentan el entorno utilizado.

## Estructura y acceso

El archivo [benchmark.csv](05_resultados/benchmark.csv) reúne las
mediciones de `cpp.csv`, `go.csv`, `java.csv` y `python.csv`.
Cada fila corresponde a una medición. Los CSV usan comas como separador
y punto decimal.

| Columna | Significado |
| --- | --- |
| `language` | Lenguaje utilizado: `cpp`, `go`, `java` o `python`. |
| `N` | Tamaño de la matriz: 500, 1000 o 1500. |
| `repetition` | Número de repetición, del 1 al 10. |
| `time_seconds` | Tiempo de multiplicación en segundos. |

El DOI de la versión publicada permite localizar y descargar el paquete
en Zenodo. Las instrucciones de reproducción están en el [README](README.md).

## Limitaciones

Las mediciones corresponden a las implementaciones, las matrices y el
equipo evaluados. Las repeticiones se realizaron con entradas fijas.
Los tiempos pueden variar al reproducir el experimento en otro equipo.

El ANOVA se interpreta como exploratorio. Los diagnósticos señalaron
diferencias de dispersión y desviaciones de la normalidad, por lo que
se omitió Tukey HSD en esta ejecución.
[Consultar el resumen del análisis](08_analisis/resumen.txt).

## Reutilización

El código se distribuye bajo la [licencia MIT](LICENSE). Los datos, tablas
y gráficos se distribuyen bajo [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Al reutilizarlos, cita al autor, la versión y el DOI de Zenodo, e indica
si realizaste cambios.
