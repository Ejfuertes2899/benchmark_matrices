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

# Benchmark de multiplicación de matrices - Pipeline

## Contenido

- [1. Descripción del experimento](#experimento)
- [2. Estructura del proyecto](#estructura)
- [3. Preparación de Windows, WSL y Docker](#preparacion)
- [4. Copia y revisión del proyecto](#copia)
- [5. Configuración del entorno de Python](#python)
- [6. Construcción de las imágenes de Docker](#imagenes)
- [7. Ejecución del flujo de trabajo](#ejecucion)
- [8. Archivos generados](#archivos)
- [9. Verificación de resultados](#verificacion)
- [10. Continuar en una nueva sesión](#nueva-sesion)
- [11. Solución de problemas](#problemas)
- [12. Documentación oficial](#documentacion)

---

<a id="experimento"></a>

## 1. Descripción del experimento

| Elemento | Configuración |
| --- | --- |
| Operación evaluada | Multiplicación de matrices |
| Lenguajes | C++, Go, Python y Java |
| Tamaños de matriz (`N`) | 500, 1000 y 1500 |
| Repeticiones por combinación de lenguaje y tamaño | 10 |
| Mediciones por lenguaje | 30 |
| Total de mediciones | **120** |
| Variable registrada | Tiempo de multiplicación en segundos |
| Entorno de ejecución | Contenedores Linux de Docker |
| Automatización | Snakemake |

El total corresponde a **4 lenguajes × 3 tamaños × 10 repeticiones = 120 mediciones**. El flujo también contempla ejecuciones de calentamiento previas a las mediciones.

**Convención de comandos:** la sección 3 indica cuándo utilizar PowerShell o Ubuntu. Desde la sección 4, todos los comandos se ejecutan en la terminal de **Ubuntu**, salvo indicación expresa. Los bloques identificados como «salida esperada» son ejemplos de resultados y no deben ejecutarse.

<a id="estructura"></a>

## 2. Estructura del proyecto

La carpeta raíz del proyecto se denomina `avance_semana4/`.

### Archivos de la carpeta raíz

| Archivo | Función |
| --- | --- |
| `README.md` | Explica cómo preparar y ejecutar el proyecto. |
| `Snakefile` | Define las tareas del flujo de trabajo y sus dependencias. |
| `requirements.txt` | Especifica las bibliotecas de Python y las versiones necesarias. |
| `.dockerignore` | Define qué archivos se excluyen del contexto de construcción de Docker. |

### Carpetas y contenido inicial

| Carpeta | Contenido |
| --- | --- |
| `01_docker/cpp/` | `Dockerfile` de C++. |
| `01_docker/go/` | `Dockerfile` de Go. |
| `01_docker/python/` | `Dockerfile` de Python. |
| `01_docker/java/` | `Dockerfile` de Java. |
| `02_caracteristicas_equipo/` | Inicialmente vacía; recibe los registros del equipo y del entorno. |
| `03_crear matrices/` | `crear_matrices.py`, `manifiesto.json` y las subcarpetas `500/`, `1000/` y `1500/`. Cada subcarpeta contiene `a.txt`, `b.txt` y `control.txt`. |
| `04_programas_matrices/` | `matrices.cpp`, `matrices.go`, `matrices.py` y `Matrices.java`. |
| `05_resultados/` | Inicialmente vacía; recibe las mediciones y los registros de ejecución. |
| `06_revisión de archivos/` | `revisar_archivos.py`. |
| `07_workflow/` | `ejecutar.py`, `integrar.py`, `analizar.py` y `registrar_equipo.py`. |
| `08_analisis/` | Inicialmente vacía; recibe las tablas estadísticas, los gráficos y el resumen. |

**Conserva los nombres de los archivos y las carpetas**, incluidos los espacios, las tildes y las mayúsculas. Cuando una ruta contiene espacios, escríbela entre comillas, como se muestra en los comandos de esta guía.

<a id="preparacion"></a>

## 3. Preparación de Windows, WSL y Docker

### 3.1. Preparar la carpeta recibida

Localiza la carpeta del avance de la semana 4. Si recibiste un archivo ZIP:

1. Haz clic derecho sobre el ZIP.
2. Selecciona **Extraer todo**.
3. Abre la carpeta extraída y localiza el contenido del proyecto.

### 3.2. Comprobar si Ubuntu está instalado

En Windows, abre **Inicio**, busca **PowerShell**, haz clic derecho y selecciona **Ejecutar como administrador**.

Ejecuta en **PowerShell**:

```powershell
wsl --list --verbose
```

Este comando muestra las distribuciones de Linux instaladas y su versión de WSL.

- Si aparece Ubuntu con `2` en la columna `VERSION`, puedes utilizar esa distribución. Conserva su nombre exacto para configurar Docker Desktop.
- Si Ubuntu no aparece o WSL todavía no está instalado, continúa con la instalación.
- Si Ubuntu aparece con `VERSION 1`, consulta la conversión a WSL 2 en el apartado 3.4.

### 3.3. Instalar Ubuntu y crear el usuario

Si necesitas instalar Ubuntu, ejecuta en **PowerShell**:

```powershell
wsl --install -d Ubuntu-24.04
```

Espera a que termine y reinicia Windows si el instalador lo solicita.

Después, abre **Ubuntu** o **Ubuntu 24.04** desde Inicio. En el primer inicio, crea el usuario y la contraseña que solicite la terminal.

**La contraseña no muestra caracteres mientras la escribes.** Es el comportamiento normal de la terminal. Recuérdala, ya que se utilizará para instalar paquetes mediante `sudo`.

### 3.4. Actualizar WSL y verificar la versión de Ubuntu

En **PowerShell como administrador**, ejecuta:

```powershell
wsl --update
wsl --list --verbose
```

Reinicia Windows si se solicita. Comprueba que Ubuntu tenga `2` en la columna `VERSION`.

Si la distribución utiliza WSL 1, puedes convertirla con el siguiente comando. Sustituye `Ubuntu-24.04` por el nombre exacto que muestre la lista:

```powershell
wsl --set-version Ubuntu-24.04 2
```

Si esa distribución ya contiene trabajo importante, respáldalo antes de convertirla. Al finalizar, vuelve a comprobar su versión con `wsl --list --verbose`.

### 3.5. Instalar e iniciar Docker Desktop

1. Abre la [página oficial de instalación de Docker Desktop para Windows](https://docs.docker.com/desktop/setup/install/windows-install/).
2. Descarga el instalador adecuado para tu equipo.
3. Ejecútalo y selecciona el motor **WSL 2** si se ofrece esa opción.
4. Completa la instalación y reinicia si se solicita.
5. Abre **Docker Desktop** desde Inicio y espera a que termine de arrancar.

Si Docker Desktop ya está instalado, ábrelo y espera a que esté listo.

### 3.6. Habilitar la integración con Ubuntu

Dentro de **Docker Desktop**:

1. Abre **Settings** mediante el icono del engranaje.
2. En **General**, comprueba que esté habilitado **Use WSL 2 based engine**, si la opción aparece.
3. Ve a **Resources → WSL Integration**.
4. Habilita la integración para la distribución de Ubuntu que utilizarás. La opción **Enable integration with my default WSL distro** corresponde a la distribución predeterminada; comprueba que sea la correcta o activa tu Ubuntu en la lista de distribuciones adicionales.
5. Pulsa **Apply** o **Apply & Restart**, según la versión.

Si no aparece la integración con WSL, comprueba que Docker Desktop esté en modo de **contenedores Linux**.

### 3.7. Comprobar Docker desde Ubuntu

Abre la terminal de **Ubuntu** y ejecuta:

```bash
docker version
```

La salida debe incluir las secciones `Client` y `Server`.

- Si el comando `docker` no se encuentra, revisa la integración con tu distribución.
- Si aparece `Client`, pero falla la conexión con `Server`, comprueba que Docker Desktop esté abierto y haya terminado de iniciar.

Verifica también el tipo de contenedores:

```bash
docker info --format '{{.OSType}}'
```

**Salida esperada:**

```text
linux
```

<a id="copia"></a>

## 4. Copia y revisión del proyecto

### 4.1. Crear y abrir la carpeta de trabajo

Ejecuta en **Ubuntu**:

```bash
mkdir -p ~/avance_semana4
cd ~/avance_semana4
pwd
```

La ruta mostrada debe ser similar a:

```text
/home/tu_usuario/avance_semana4
```

El comando `mkdir -p` puede terminar sin mostrar mensajes; esto es normal.

Para abrir la carpeta actual en el Explorador de Windows, ejecuta:

```bash
explorer.exe .
```

### 4.2. Copiar el contenido del proyecto

Utiliza dos ventanas del Explorador:

| Ventana | Ubicación |
| --- | --- |
| Origen | La carpeta `avance_semana4` que recibiste y extrajiste. |
| Destino | La carpeta de Ubuntu que acabas de abrir con `explorer.exe .`. |

En la ventana de origen:

1. Abre la carpeta que contiene directamente `Snakefile`, `requirements.txt`, `.dockerignore`, `README.md` y las carpetas del proyecto.
2. Pulsa **Ctrl + A** para seleccionar su contenido y **Ctrl + C** para copiarlo.
3. Regresa a la ventana de destino y pulsa **Ctrl + V**.

**Copia el contenido de la carpeta**, de modo que `Snakefile` quede directamente en `~/avance_semana4/`. Evita crear una carpeta adicional como `~/avance_semana4/avance_semana4/`.

### 4.3. Revisar los archivos copiados

Regresa a Ubuntu y ejecuta:

```bash
ls -a
```

Comprueba que aparecen los archivos y las carpetas descritos en la [estructura del proyecto](#estructura). La opción `-a` permite ver también `.dockerignore`.

Verifica los cuatro scripts del flujo de trabajo:

```bash
ls -l 07_workflow
```

Deben aparecer:

- `ejecutar.py`
- `integrar.py`
- `analizar.py`
- `registrar_equipo.py`

Si no se lista ninguno de estos archivos, revisa la copia antes de continuar.

### 4.4. Revisar las rutas del Snakefile

Muestra las primeras doce líneas:

```bash
head -n 12 Snakefile
```

Comprueba que las rutas de salida estén configuradas de la siguiente manera:

```python
RESULTADOS = "05_resultados"
ANALISIS = "08_analisis"
CARACTERISTICAS = "02_caracteristicas_equipo"
```

Este bloque representa la configuración del archivo; **no es un comando para la terminal**. Si las variables no aparecen entre las primeras doce líneas, búscalas en el resto del `Snakefile`.

<a id="python"></a>

## 5. Configuración del entorno de Python

### 5.1. Instalar Python y las herramientas del entorno

Actualiza la lista de paquetes disponibles:

```bash
sudo apt update
```

Instala las herramientas necesarias:

```bash
sudo apt install -y python3 python3-venv python3-pip
```

| Paquete | Función |
| --- | --- |
| `python3` | Ejecuta los programas de Python. |
| `python3-venv` | Permite crear un entorno virtual para el proyecto. |
| `python3-pip` | Permite instalar bibliotecas de Python. |

Espera a que termine la instalación y comprueba la versión:

```bash
python3 --version
```

### 5.2. Crear y activar el entorno virtual

Crea una carpeta para los entornos de Python y el entorno de este proyecto:

```bash
mkdir -p ~/entornos
python3 -m venv ~/entornos/semana4
```

Las ubicaciones cumplen funciones diferentes:

| Ruta | Contenido |
| --- | --- |
| `~/avance_semana4` | Archivos del proyecto. |
| `~/entornos/semana4` | Intérprete y bibliotecas del entorno virtual. |

Activa el entorno:

```bash
source ~/entornos/semana4/bin/activate
```

Normalmente aparecerá `(semana4)` al principio de la línea de la terminal:

```text
(semana4) usuario@equipo:~/avance_semana4$
```

### 5.3. Instalar las dependencias del proyecto

Con el entorno activo y desde la carpeta del proyecto, ejecuta:

```bash
cd ~/avance_semana4
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

El último comando instala las bibliotecas y versiones indicadas en `requirements.txt`.

### 5.4. Verificar la instalación

Comprueba la versión de Snakemake y la compatibilidad de las dependencias:

```bash
snakemake --version
python -m pip check
```

Snakemake debe mostrar su versión. Si no hay conflictos de dependencias, `pip check` muestra:

```text
No broken requirements found.
```

<a id="imagenes"></a>

## 6. Construcción de las imágenes de Docker

Mantén **Docker Desktop abierto** y ejecuta los siguientes comandos desde `~/avance_semana4`. Espera a que cada construcción termine correctamente antes de continuar.

El punto final (`.`) indica que la carpeta actual es el contexto de construcción; forma parte del comando.

### 6.1. Imagen de C++

```bash
docker build -f 01_docker/cpp/Dockerfile -t matrices-cpp:semana4 .
```

### 6.2. Imagen de Go

```bash
docker build -f 01_docker/go/Dockerfile -t matrices-go:semana4 .
```

### 6.3. Imagen de Python

```bash
docker build -f 01_docker/python/Dockerfile -t matrices-python:semana4 .
```

### 6.4. Imagen de Java

```bash
docker build -f 01_docker/java/Dockerfile -t matrices-java:semana4 .
```

### 6.5. Verificar las cuatro imágenes

```bash
docker image inspect --format '{{.RepoTags}}' \
  matrices-cpp:semana4 \
  matrices-go:semana4 \
  matrices-python:semana4 \
  matrices-java:semana4
```

Las barras invertidas (`\`) permiten continuar el comando en la línea siguiente. Puedes copiar el bloque completo en Ubuntu.

**Salida esperada:**

```text
[matrices-cpp:semana4]
[matrices-go:semana4]
[matrices-python:semana4]
[matrices-java:semana4]
```

<a id="ejecucion"></a>

## 7. Ejecución del flujo de trabajo

### 7.1. Realizar la revisión inicial

Con el entorno virtual activo, ejecuta:

```bash
python "06_revisión de archivos/revisar_archivos.py"
```

En una copia inicial sin resultados previos, el contador esperado es:

```text
Total: 0/120 mediciones válidas.
```

Este contador indica que todavía no hay mediciones registradas. **Por sí solo no confirma que las entradas sean correctas**: revisa también los demás mensajes del script y resuelve los errores que señale antes de ejecutar el experimento. Si ya existen resultados, el contador puede ser diferente.

### 7.2. Simular la ejecución

```bash
snakemake --cores 1 --dry-run
```

La opción `--dry-run` muestra las tareas previstas sin ejecutar el experimento. Para una ejecución inicial, las reglas esperadas son:

| Regla | Función en el flujo |
| --- | --- |
| `ejecutar_contenedores` | Ejecutar la fase experimental en los contenedores. |
| `integrar` | Unificar las mediciones. |
| `analizar` | Generar el análisis estadístico y sus productos. |
| `all` | Agrupar los objetivos finales del flujo. |

Si las salidas ya existen y están actualizadas, Snakemake puede indicar que no hay tareas pendientes.

### 7.3. Ejecutar el experimento

```bash
snakemake --cores 1 --rerun-incomplete
```

La opción `--rerun-incomplete` permite volver a ejecutar las tareas cuyas salidas Snakemake reconoce como incompletas.

El flujo está preparado para:

1. Comprobar las entradas y las imágenes de Docker.
2. Registrar las características del equipo y las versiones en `02_caracteristicas_equipo/`.
3. Ejecutar los calentamientos y las mediciones.
4. Generar los cuatro archivos CSV individuales.
5. Integrar las mediciones en `05_resultados/benchmark.csv`.
6. Generar las tablas, los gráficos y el resumen en `08_analisis/`.

**Mantén `--cores 1` para seguir la configuración de esta guía.** Esta opción controla la planificación de Snakemake; no establece por sí sola un límite de CPU para cada contenedor.

<a id="archivos"></a>

## 8. Archivos generados

La salida prevista comprende **23 archivos principales**, distribuidos en tres carpetas:

| Carpeta | Cantidad | Contenido |
| --- | ---: | --- |
| `02_caracteristicas_equipo/` | 6 | Equipo, versiones e imágenes utilizadas. |
| `05_resultados/` | 8 | Mediciones y trazabilidad de la ejecución. |
| `08_analisis/` | 9 | Tablas estadísticas, gráficos y resumen. |
| **Total** | **23** | |

### 8.1. Características del equipo y del entorno

**Carpeta:** `02_caracteristicas_equipo/`

| Archivo | Contenido |
| --- | --- |
| `caracteristicas_equipo.txt` | CPU, RAM, sistemas operativos, recursos de Docker y configuración del experimento. |
| `versiones_lenguajes.txt` | Versiones de `g++`, Go, Python, Java y `javac` dentro de las imágenes. |
| `python_workflow.txt` | Identificación del intérprete de Python que ejecuta el flujo de trabajo. |
| `snakemake_version.txt` | Versión de Snakemake. |
| `docker_version.txt` | Versiones del cliente y del servidor de Docker. |
| `imagenes.json` | Imágenes utilizadas y fecha de captura de la información. |

### 8.2. Mediciones y registros de ejecución

**Carpeta:** `05_resultados/`

| Archivo | Contenido |
| --- | --- |
| `cpp.csv` | Las 30 mediciones de C++: diez por tamaño. |
| `go.csv` | Las 30 mediciones de Go: diez por tamaño. |
| `python.csv` | Las 30 mediciones de Python: diez por tamaño. |
| `java.csv` | Las 30 mediciones de Java: diez por tamaño. |
| `benchmark.csv` | Las 120 mediciones integradas para el análisis. |
| `orden.csv` | Orden de los bloques y semilla utilizada. |
| `imagenes.json` | Identificación de las imágenes asociadas a las mediciones. |
| `ejecucion.log` | Mensajes y tiempos informados durante la fase experimental. |

Los CSV de mediciones utilizan las siguientes columnas:

| Columna | Significado |
| --- | --- |
| `language` | Lenguaje de programación utilizado. |
| `N` | Tamaño de las matrices. |
| `repetition` | Número de repetición, del 1 al 10. |
| `time_seconds` | Tiempo de multiplicación en segundos. |

### 8.3. Análisis estadístico

**Carpeta:** `08_analisis/`

| Archivo | Contenido |
| --- | --- |
| `descriptivos.csv` | Resumen de tiempos mediante media, mediana, desviación, mínimo y máximo. |
| `anova.csv` | ANOVA de los efectos de lenguaje, tamaño e interacción sobre los tiempos en segundos. |
| `anova_log.csv` | ANOVA sobre el logaritmo del tiempo; corresponde al modelo principal configurado. |
| `supuestos.csv` | Comprobaciones de normalidad de los residuos y homogeneidad de varianzas. |
| `tukey.csv` | Comparaciones entre combinaciones de lenguaje y tamaño, cuando corresponde realizarlas. |
| `resumen.txt` | Explicación de los resultados principales e indicación de si se realizaron comparaciones de Tukey. |
| `cajas.png` | Distribución de los tiempos por lenguaje y tamaño. |
| `interaccion.png` | Variación de las medias de cada lenguaje al aumentar el tamaño. |
| `diagnostico.png` | Gráficos para revisar los supuestos del análisis. |

La realización de las comparaciones de Tukey debe comprobarse en `resumen.txt`; la presencia de `tukey.csv` por sí sola no confirma que se hayan calculado comparaciones.

### 8.4. Archivos auxiliares

Además de las salidas principales, pueden generarse las siguientes carpetas:

| Carpeta | Función |
| --- | --- |
| `.snakemake/` | Almacena registros y metadatos internos para gestionar las ejecuciones. |
| `__pycache__/` | Almacena archivos de caché que Python crea al importar módulos. |

<a id="verificacion"></a>

## 9. Verificación de resultados

### 9.1. Comprobar las 120 mediciones

```bash
python "06_revisión de archivos/revisar_archivos.py" --completo
```

**Salida esperada:**

```text
Total: 120/120 mediciones válidas.
```

### 9.2. Revisar el archivo integrado

Ejecuta este bloque completo en Ubuntu:

```bash
python - <<'PY'
import pandas as pd

datos = pd.read_csv("05_resultados/benchmark.csv")
print(datos.groupby(["language", "N"]).size())
print("Total:", len(datos))
PY
```

La salida debe mostrar **10 mediciones por cada combinación de lenguaje y tamaño**: doce combinaciones en total. La última línea debe ser:

```text
Total: 120
```

### 9.3. Comprobar los productos del análisis

```bash
ls -lh 08_analisis
```

Comprueba que aparecen los nueve archivos descritos en el apartado 8.3:

```text
descriptivos.csv
anova.csv
anova_log.csv
supuestos.csv
tukey.csv
resumen.txt
cajas.png
interaccion.png
diagnostico.png
```

### 9.4. Leer el resumen

```bash
cat 08_analisis/resumen.txt
```

El resumen explica los principales resultados del análisis y señala si se realizaron las comparaciones de Tukey.

### 9.5. Abrir los resultados en Windows

Desde la carpeta del proyecto, ejecuta:

```bash
explorer.exe .
```

En el Explorador podrás revisar los registros en `02_caracteristicas_equipo/`, las mediciones en `05_resultados/` y las tablas y figuras en `08_analisis/`.

### Lista de comprobación final

- [ ] El flujo terminó sin errores.
- [ ] La revisión completa informa `120/120 mediciones válidas`.
- [ ] `benchmark.csv` contiene 120 filas de mediciones.
- [ ] Cada combinación de lenguaje y tamaño contiene 10 mediciones.
- [ ] Se generaron los registros del equipo y del entorno.
- [ ] Se revisaron las tablas y los gráficos de `08_analisis/`.
- [ ] Se leyó `resumen.txt` y se comprobó si se realizaron comparaciones de Tukey.
      
<a id="problemas"></a>

## 10. Solución de problemas

| Situación | Qué revisar |
| --- | --- |
| `docker` no se encuentra en Ubuntu. | Habilita la integración de Docker Desktop con la distribución de Ubuntu que estás utilizando. |
| `docker version` muestra el cliente, pero no conecta con el servidor. | Abre Docker Desktop y espera a que termine de iniciar. |
| El tipo de contenedores no es `linux`. | Cambia Docker Desktop al modo de contenedores Linux y vuelve a comprobarlo. |
| No se encuentra `Snakefile` o `requirements.txt`. | Ejecuta `cd ~/avance_semana4` y revisa `ls -a`. Comprueba que no hayas copiado el proyecto dentro de una carpeta adicional. |
| Faltan los scripts de `07_workflow/`. | Revisa la copia y confirma que estén los cuatro archivos indicados en la estructura. |
| `snakemake` no se encuentra. | Activa `~/entornos/semana4` y confirma que la instalación con `requirements.txt` terminó correctamente. |
| `python -m pip check` informa conflictos. | Revisa los mensajes y las versiones indicadas en `requirements.txt` antes de continuar. |
| Falta alguna imagen `matrices-*:semana4`. | Ejecuta el comando de construcción correspondiente y revisa su salida. |
| Una ruta con espacios no se reconoce. | Conserva las comillas, los espacios y las tildes tal como aparecen en la guía. |
| La revisión inicial muestra `0/120`. | Es lo esperado si todavía no se ha ejecutado el experimento; revisa también el resto de los mensajes del verificador. |
| La revisión final muestra menos de 120 mediciones válidas. | Revisa la salida de Snakemake y `05_resultados/ejecucion.log`; corrige el error antes de volver a ejecutar el flujo. |
| Snakemake indica que no hay tareas pendientes. | Comprueba si las salidas ya existen y están actualizadas; esto no implica un fallo. |

> **Importante:** Mantén Docker Desktop iniciado durante toda la ejecución del pipeline. Puedes minimizar su ventana, pero no salir de la aplicación hasta que termine el proceso.

>  **Importante:** Antes de la primera ejecución, las carpetas `02_caracteristicas_equipo`, `05_resultados` y `08_analisis` deben contener únicamente su archivo `.gitkeep`.
> Estos archivos permiten conservar las carpetas en GitHub. Pueden permanecer durante la ejecución, ya que no afectan al funcionamiento del pipeline ni a los resultados del experimento.


