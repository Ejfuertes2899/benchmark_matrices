# Benchmark reproducible de multiplicación de matrices

## 1. Objetivo

Diseñar y desarrollar un experimento computacional reproducible que permita comparar el tiempo de ejecución del algoritmo naive de multiplicación de matrices cuadradas N × N implementado en C++, Go, Java y Python.

## 2. Pregunta de investigación

¿Existen diferencias estadísticamente significativas en el tiempo de ejecución del algoritmo naive de multiplicación de matrices N × N entre implementaciones equivalentes desarrolladas en C++, Go, Java y Python, y cómo varían estas diferencias según el tamaño de la matriz?

## 3. Hipótesis

- **Hipótesis nula (H₀):** El lenguaje de implementación no produce diferencias estadísticamente significativas en el tiempo de ejecución del algoritmo de multiplicación de matrices.
- **Hipótesis alternativa (H₁):** Al menos uno de los lenguajes presenta un tiempo de ejecución significativamente diferente de los demás.

## 4. Variables

| Tipo | Variable | Valores o unidad de medida |
| :--- | :--- | :--- |
| Independiente | Lenguaje de programación | C++, Go, Java y Python |
| Independiente | Tamaño de la matriz (N) | 500, 1000 y 1500 |
| Dependiente | Tiempo de ejecución de la multiplicación | Segundos |

**Condiciones controladas:**

- Mismo equipo y sistema operativo.
- Mismas matrices de entrada para cada tamaño.
- Mismo algoritmo y orden de los bucles.
- Misma precisión numérica.
- Mismo criterio de medición del tiempo.
- Ejecución sin paralelización y sin otras tareas intensivas simultáneas.

Se registrarán el procesador, la memoria RAM, el sistema operativo, la arquitectura y las versiones de los lenguajes, compiladores o máquinas virtuales utilizados.

## 5. Diseño experimental

### 5.1. Configuración del experimento

Se utilizará un **diseño factorial de dos factores**, combinando los cuatro lenguajes con los tres tamaños de matriz.

- **Lenguajes:** C++, Go, Java y Python.
- **Tamaños:** N = 500, 1000 y 1500.
- **Repeticiones:** 10 por cada combinación de lenguaje y tamaño.

En total, se realizarán **120 mediciones**:

**4 lenguajes × 3 tamaños × 10 repeticiones = 120 mediciones.**

### 5.2. Datos de entrada e implementaciones

Se generará una pareja de matrices por tamaño, una sola vez, utilizando una **semilla fija y documentada**. Las matrices se guardarán en archivos que compartirán los cuatro programas y se reutilizarán en todas las repeticiones.

Así se garantizarán entradas idénticas, sin depender de que los generadores aleatorios de los distintos lenguajes produzcan los mismos valores.

Las cuatro implementaciones utilizarán:

- El algoritmo naive de multiplicación de matrices.
- El mismo orden de los tres bucles.
- Números de doble precisión (64 bits).
- Ninguna librería optimizada para multiplicación de matrices ni paralelización.

### 5.3. Procedimiento de ejecución

Las pruebas se ejecutarán en el mismo equipo, un programa a la vez. Se aleatorizará el orden de las pruebas para reducir posibles efectos del orden de ejecución.

Para cada combinación de lenguaje y tamaño, se realizarán ejecuciones de calentamiento que no formarán parte de las 10 mediciones.

En cada repetición medida se seguirá este procedimiento:

1. **Preparar los datos:** cargar las matrices de entrada y preparar la matriz de salida antes de iniciar el temporizador.
2. **Iniciar la medición:** iniciar el temporizador justo antes de multiplicar las matrices.
3. **Ejecutar la multiplicación:** calcular la matriz resultante y detener el temporizador inmediatamente al terminar.
4. **Registrar el tiempo:** guardar la duración de la multiplicación en segundos.

La medición excluirá la generación y carga de las matrices, la compilación, el calentamiento, la validación y la escritura de resultados.

Se documentarán también las opciones de compilación y ejecución utilizadas.

### 5.4. Registro de resultados

Cada lenguaje generará su propio archivo de resultados:

- **C++:** `cpp.csv`
- **Go:** `go.csv`
- **Java:** `java.csv`
- **Python:** `python.csv`

Los cuatro archivos tendrán la misma estructura:

| Columna | Descripción |
| :--- | :--- |
| `language` | Lenguaje de programación utilizado |
| `N` | Tamaño de la matriz |
| `repetition` | Número de repetición, del 1 al 10 |
| `time_seconds` | Tiempo de multiplicación en segundos |

### 5.5. Análisis previsto

Se calcularán la **media** y la **desviación estándar** del tiempo de ejecución para cada combinación de lenguaje y tamaño.

Se revisarán los supuestos del **ANOVA de dos factores con interacción** antes de aplicarlo. Este análisis permitirá evaluar:

- El efecto del lenguaje de programación.
- El efecto del tamaño de la matriz.
- Si las diferencias entre lenguajes cambian según el tamaño de la matriz.

Se utilizará un **nivel de significancia de 0,05** y se realizarán comparaciones **Tukey HSD** cuando corresponda.

# Experimento de matrices con Docker

## Contenido

1. [Preparar el proyecto](#1-preparar-el-proyecto)
2. [Configurar WSL 2](#2-configurar-wsl-2)
3. [Instalar Docker Desktop](#3-instalar-docker-desktop)
4. [Abrir PowerShell en el proyecto](#4-abrir-powershell-en-el-proyecto)
5. [Comprobar Docker](#5-comprobar-docker)
6. [Preparar la carpeta de resultados](#6-preparar-la-carpeta-de-resultados)
7. [Comprobar las matrices](#7-comprobar-las-matrices)
8. [Construir las imágenes Docker](#8-construir-las-imágenes-docker)
9. [Registrar las versiones](#9-registrar-las-versiones)
10. [Realizar una prueba individual](#10-realizar-una-prueba-individual)
11. [Consultar el orden de las pruebas](#11-consultar-el-orden-de-las-pruebas)
12. [Ejecutar el experimento](#12-ejecutar-el-experimento)
13. [Verificar la finalización](#13-verificar-la-finalización)
14. [Consultar los resultados](#14-consultar-los-resultados)

## 1. Preparar el proyecto

1. Abre el repositorio del proyecto en GitHub.
2. Selecciona **Code → Download ZIP**.
3. Extrae todo el contenido del archivo ZIP.
4. Abre la carpeta extraída que contiene los siguientes elementos:

| Carpeta o archivo | Función |
| --- | --- |
| `01_docker` | Contiene las instrucciones para preparar y ejecutar los programas con Docker.|
| `02_caracteristicas_equipo` | Guarda las versiones de las herramientas y el orden de las pruebas. |
| `03_crear matrices` | Contiene las matrices, sus controles y el programa para generarlas. |
| `04_programas_matrices` | Contiene las implementaciones en los cuatro lenguajes. |
| `05_resultados` | Recibe los cuatro archivos CSV de la ejecución. |
| `06_revisión de archivos` | Contiene el programa que comprueba las entradas y los resultados. |
| `ejecutar_experimento.ps1` | Organiza y ejecuta el experimento completo. |
| `capturar_versiones.ps1` | Guarda las versiones de los lenguajes y de Docker. |
| `.dockerignore` | Indica qué archivos se excluyen al construir las imágenes. |

> **Importante:** conserva los nombres de las carpetas y los archivos, incluidos sus espacios y tildes. Los programas utilizan esas rutas.

## 2. Configurar WSL 2

WSL 2 permite utilizar el entorno Linux de Docker desde Windows.

1. Abre el menú **Inicio** y busca **PowerShell**.
2. Haz clic derecho y selecciona **Ejecutar como administrador**.
3. Acepta la solicitud de Windows.
4. Comprueba si WSL está instalado:

```powershell
wsl --version
```

**Si aparecen los datos de versión**, actualiza WSL:

```powershell
wsl --update
```

**Si WSL no está instalado**, ejecuta:

```powershell
wsl --install --no-distribution
```

Reinicia el equipo si se solicita. Después, vuelve a abrir PowerShell como administrador y ejecuta:

```powershell
wsl --update
```

Finalmente, establece WSL 2 como versión predeterminada:

```powershell
wsl --set-default-version 2
```

La opción `--no-distribution` instala WSL sin añadir una distribución como Ubuntu. Al terminar, puedes cerrar la ventana de administrador.

## 3. Instalar Docker Desktop

Docker proporciona los entornos donde se ejecutarán los programas del experimento.

1. Descarga el instalador desde la [página oficial de Docker Desktop para Windows](https://docs.docker.com/desktop/setup/install/windows-install/).
2. Selecciona la versión correspondiente a tu equipo. Para procesadores Intel o AMD de 64 bits, utiliza **x86_64**.
3. Ejecuta el instalador y selecciona **WSL 2** si permite elegir el entorno.
4. Completa la instalación y reinicia si se solicita.
5. Abre **Docker Desktop** y espera a que el motor esté funcionando.

El proyecto utiliza **contenedores Linux**, que se ejecutan en Windows mediante Docker Desktop con WSL 2.

No necesitas instalar C++, Go, Python o Java directamente en Windows: las herramientas necesarias estarán dentro de las imágenes Docker.

- **Imagen:** entorno preparado y guardado.
- **Contenedor:** una ejecución de ese entorno.

## 4. Abrir PowerShell en el proyecto

1. Abre la carpeta del proyecto en el **Explorador de archivos**.
2. Haz clic en la barra de direcciones, escribe `powershell` y presiona **Enter**.
3. Comprueba la ubicación actual:

```powershell
Get-Location
```

4. Muestra el contenido de la carpeta:

```powershell
Get-ChildItem
```

Debes ver las carpetas numeradas y los archivos `ejecutar_experimento.ps1` y `capturar_versiones.ps1`.

5. Permite la ejecución de los scripts en esta sesión:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
```

> Este ajuste solo afecta a la ventana actual de PowerShell y desaparece al cerrarla. Mantén esta ventana abierta para los siguientes pasos.

## 5. Comprobar Docker

Consulta la versión de Docker:

```powershell
docker version
```

Debes ver información del cliente (**Client**) y del servidor (**Server**).

Comprueba el tipo de contenedores:

```powershell
docker info --format "{{.OSType}}"
```

El resultado esperado es:

```text
linux
```

Esto confirma que Docker está disponible y utiliza contenedores Linux.

## 6. Preparar la carpeta de resultados

Antes de iniciar una nueva sesión, abre `05_resultados` y comprueba que no contenga resultados anteriores:

- `cpp.csv`
- `go.csv`
- `python.csv`
- `java.csv`

Si existen, retíralos de la carpeta de trabajo. Si deseas conservarlos, muévelos a otra ubicación.

> **Importante:** retira únicamente los CSV de ejecuciones anteriores y conserva la carpeta `05_resultados`. Así evitarás mezclar mediciones de distintas sesiones.

## 7. Comprobar las matrices

Las matrices son tablas de números que utilizarán los cuatro programas. Abre `03_crear matrices` y verifica que existan estas subcarpetas:

| Subcarpeta | Tamaño de las matrices |
| --- | --- |
| `500` | 500 × 500 |
| `1000` | 1000 × 1000 |
| `1500` | 1500 × 1500 |

Cada subcarpeta debe contener:

| Archivo | Contenido |
| --- | --- |
| `a.txt` | Primera matriz. |
| `b.txt` | Segunda matriz. |
| `control.txt` | Valores de referencia para comprobar la multiplicación. |

También debe existir `manifiesto.json`, que permite comprobar que las entradas corresponden a las esperadas.

### Generar las matrices si faltan

Desde la misma ventana de PowerShell, guarda la ruta del proyecto:

```powershell
$proyecto = (Get-Location).Path
```

Ejecuta el generador incluido:

```powershell
docker run --rm --mount "type=bind,source=$proyecto,target=/app" --workdir /app python:3.11.17-slim-bookworm python "03_crear matrices/crear_matrices.py"
```

La primera vez, Docker puede descargar la imagen de Python. Después, el programa creará las matrices, los controles y el manifiesto.

Al finalizar, debe aparecer:

```text
Matrices y manifiesto preparados.
```

## 8. Construir las imágenes Docker

Cada lenguaje utiliza un entorno independiente. Las imágenes deben construirse en tu equipo, aunque ya hayas descargado todos los archivos del proyecto.

Ejecuta los comandos **uno por uno**, esperando a que termine cada construcción.

### C++

```powershell
docker build -f ".\01_docker\cpp\Dockerfile" -t matrices-cpp:semana3 .
```

### Go

```powershell
docker build -f ".\01_docker\go\Dockerfile" -t matrices-go:semana3 .
```

### Python

```powershell
docker build -f ".\01_docker\python\Dockerfile" -t matrices-python:semana3 .
```

### Java

```powershell
docker build -f ".\01_docker\java\Dockerfile" -t matrices-java:semana3 .
```

> **No omitas el punto final (`.`):** indica que Docker debe utilizar los archivos de la carpeta actual como contexto de construcción.

Comprueba que las cuatro imágenes estén disponibles:

```powershell
docker image ls --filter "reference=matrices-*:semana3"
```

Debes encontrar:

| Imagen | Etiqueta |
| --- | --- |
| `matrices-cpp` | `semana3` |
| `matrices-go` | `semana3` |
| `matrices-python` | `semana3` |
| `matrices-java` | `semana3` |

## 9. Registrar las versiones

Estos registros permiten identificar las herramientas y las imágenes utilizadas en tu ejecución.

### Versión de Docker

```powershell
.\capturar_versiones.ps1 -Tipo Docker
```

Crea o actualiza `02_caracteristicas_equipo/docker_version.txt`.

### Versiones de los lenguajes

```powershell
.\capturar_versiones.ps1 -Tipo Lenguajes
```

Crea o actualiza `02_caracteristicas_equipo/versiones_lenguajes.txt`, con información de C++, Go, Python, Java y el compilador de Java.

### Registro de las imágenes

```powershell
docker image inspect matrices-cpp:semana3 matrices-go:semana3 matrices-python:semana3 matrices-java:semana3 | Out-File -FilePath ".\02_caracteristicas_equipo\imagenes.json" -Encoding utf8
```

Actualiza `02_caracteristicas_equipo/imagenes.json` con la información de las imágenes construidas en tu equipo.

## 10. Realizar una prueba individual

**Paso opcional.** Permite comprobar C++ con matrices de tamaño `500` sin utilizar la carpeta de resultados definitivos.

Crea una carpeta temporal:

```powershell
$prueba = Join-Path $env:TEMP ("prueba_matrices_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
New-Item -ItemType Directory -Path $prueba | Out-Null
```

Ejecuta la prueba:

```powershell
docker run --rm --cpus=1 --mount "type=bind,source=$prueba,target=/app/06_resultados" matrices-cpp:semana3 500
```

El programa realizará **2 calentamientos y 10 mediciones**.

Para consultar el CSV:

```powershell
Get-Content -LiteralPath (Join-Path $prueba "cpp.csv")
```

Para abrir la carpeta que lo contiene:

```powershell
Invoke-Item -LiteralPath $prueba
```

El archivo permanece en la carpeta temporal de Windows cuando termina el contenedor y no se mezcla con los resultados de `05_resultados`.

## 11. Consultar el orden de las pruebas

**Paso opcional.** Muestra el orden planificado de ejecución:

```powershell
.\ejecutar_experimento.ps1 -SoloOrden
```

Aparecerá una tabla con **12 bloques**. Cada bloque combina un lenguaje y un tamaño de matriz; por ejemplo, C++ con tamaño `1500` o Go con tamaño `1000`.

El proyecto utiliza la semilla **`2027`** para generar el orden aleatorizado. Una semilla permite volver a obtener el mismo orden.

## 12. Ejecutar el experimento

Antes de comenzar, comprueba lo siguiente:

- [ ] Docker Desktop está abierto y el motor está funcionando.
- [ ] El equipo está conectado a la corriente.
- [ ] No se están ejecutando otras tareas exigentes.
- [ ] La carpeta `05_resultados` no contiene CSV anteriores.
- [ ] PowerShell permanece abierto en la carpeta del proyecto.
- [ ] El equipo no entrará en suspensión durante las pruebas.

Espera a que termine el experimento para abrir los CSV.

Inicia la ejecución:

```powershell
.\ejecutar_experimento.ps1
```

El programa realizará automáticamente estas tareas:

1. Comprobar las carpetas y las cuatro imágenes Docker.
2. Verificar que `05_resultados` no contenga CSV anteriores.
3. Generar el orden de ejecución con la semilla `2027`.
4. Guardar la semilla y el orden planificado en `02_caracteristicas_equipo`.
5. Ejecutar los 12 bloques, uno después del otro.
6. Comprobar los resultados al finalizar.

> En cada bloque se realizan **2 calentamientos y 10 mediciones**. Los calentamientos no se incluyen en los CSV.

## 13. Verificar la finalización

Al terminar correctamente, deben aparecer estos mensajes:

```text
Total: 120/120 mediciones válidas.
```

```text
Experimento completo: 120 mediciones validas.
```

Esto indica que se completaron las 12 combinaciones y que los resultados pasaron las comprobaciones del verificador.

Si aparece un error, la ejecución se detiene y conserva los resultados parciales.

## 14. Consultar los resultados

### Archivos generados

Abre `05_resultados`. Debes encontrar:

| Archivo | Contenido | Mediciones |
| --- | --- | ---: |
| `cpp.csv` | Resultados de C++. | 30 |
| `go.csv` | Resultados de Go. | 30 |
| `python.csv` | Resultados de Python. | 30 |
| `java.csv` | Resultados de Java. | 30 |
| **Total** | **Cuatro lenguajes.** | **120** |

Cada archivo contiene **30 mediciones más una fila de encabezado**: 10 mediciones para cada uno de los 3 tamaños.

### Columnas de los CSV

Los cuatro archivos utilizan las mismas columnas:

| Columna | Significado |
| --- | --- |
| `language` | Lenguaje utilizado. |
| `N` | Número de filas y columnas de las matrices. |
| `repetition` | Número de medición, del 1 al 10 para cada tamaño. |
| `time_seconds` | Tiempo de la multiplicación, en segundos. |

### Registros de la ejecución

En `02_caracteristicas_equipo` también encontrarás:

- `docker_version.txt`: versión de Docker.
- `versiones_lenguajes.txt`: versiones de los lenguajes y compiladores registrados.
- `imagenes.json`: información de las imágenes utilizadas.
- Un archivo CSV cuyo nombre comienza por `orden_ejecucion_semilla_2027_`: orden planificado de los 12 bloques.
