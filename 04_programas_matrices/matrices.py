
from array import array
from pathlib import Path
import csv
import sys
from time import perf_counter

CALENTAMIENTOS = 2
REPETICIONES = 10


def cargar_matriz(ruta, n):
    """Carga N x N valores double de 64 bits antes de medir."""
    with ruta.open(encoding="ascii") as archivo:
        if int(archivo.readline()) != n:
            raise ValueError("El tamaño del archivo no coincide.")
        datos = array("d", (float(valor) for linea in archivo for valor in linea.split()))
    if datos.itemsize != 8 or len(datos) != n * n:
        raise ValueError("La matriz debe contener N por N números de 64 bits.")
    return datos


def multiplicar(a, b, c, n):
    """Calcula C = A x B con el orden fila, columna, paso."""
    for fila in range(n):
        for columna in range(n):
            suma = 0.0
            for paso in range(n):
                suma += a[fila * n + paso] * b[paso * n + columna]
            c[fila * n + columna] = suma


def validar(c, n, control):
    """Comprueba la suma total y tres celdas con el reloj detenido."""
    centro = (n // 2) * n + n // 2
    obtenido = [sum(c), c[0], c[centro], c[-1]]
    if obtenido != control:
        raise ValueError("La multiplicación no pasó la validación.")


def principal():
    """Realiza dos calentamientos y diez mediciones para un tamaño."""
    # 1. Revisar el argumento y evitar mediciones duplicadas.
    if len(sys.argv) != 2 or sys.argv[1] not in ("500", "1000", "1500"):
        raise ValueError(
            "Uso: python 04_programas_matrices/matrices.py 500 (o 1000 o 1500)"
        )
    n = int(sys.argv[1])
    raiz = Path(__file__).resolve().parents[1]
    carpeta = raiz / "03_crear matrices" / str(n)
    salida = raiz / "06_resultados" / "python.csv"
    cabecera = ["language", "N", "repetition", "time_seconds"]
    if salida.exists() and salida.stat().st_size > 0:
        with salida.open(newline="", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            if lector.fieldnames != cabecera:
                raise ValueError("El CSV tiene un encabezado diferente.")
            if any(fila["N"] == str(n) for fila in lector):
                raise ValueError(
                    "Este tamaño ya tiene filas. Conserva los CSV antes de repetir."
                )

    # 2. Cargar las entradas y sus referencias antes de medir.
    a = cargar_matriz(carpeta / "a.txt", n)
    b = cargar_matriz(carpeta / "b.txt", n)
    valores = (carpeta / "control.txt").read_text(encoding="ascii").split()
    if len(valores) != 5 or int(valores[0]) != n:
        raise ValueError("El archivo de control no corresponde a este tamaño.")
    control = [float(valor) for valor in valores[1:]]

    # 3. Preparar el CSV y C fuera del intervalo medido.
    salida.parent.mkdir(parents=True, exist_ok=True)
    nuevo = not salida.exists() or salida.stat().st_size == 0
    # El algoritmo sobrescribe toda C en cada multiplicación.
    c = array("d", [0.0]) * (n * n)
    with salida.open("a", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo, lineterminator="\n")
        if nuevo:
            escritor.writerow(cabecera)

        # 4. Hacer dos calentamientos y guardar las diez mediciones siguientes.
        for ejecucion in range(1, CALENTAMIENTOS + REPETICIONES + 1):
            # La preparación, validación y escritura quedan fuera de este intervalo.
            inicio = perf_counter()
            multiplicar(a, b, c, n)
            fin = perf_counter()
            segundos = fin - inicio
            validar(c, n, control)
            if ejecucion > CALENTAMIENTOS:
                repeticion = ejecucion - CALENTAMIENTOS
                escritor.writerow(["python", n, repeticion, f"{segundos:.9f}"])
                archivo.flush()
                print(
                    f"python | N={n} | repetición={repeticion} | {segundos:.9f} s",
                    flush=True,
                )
            else:
                print(f"python | N={n} | calentamiento {ejecucion}/2", flush=True)


if __name__ == "__main__":
    try:
        principal()
    except (OSError, ValueError, KeyError) as error:
        sys.exit(f"Error: {error}")
