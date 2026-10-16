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
