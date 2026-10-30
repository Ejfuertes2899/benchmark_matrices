"""Prepara entradas reproducibles y sus referencias, sin medir tiempos."""

from pathlib import Path
import csv
import hashlib
import json
import random
import sys

RAIZ = Path(__file__).resolve().parents[1]
MATRICES = RAIZ / "03_crear matrices"
# En el proyecto se usa 05; las imagenes Docker conservan su ruta interna.
RESULTADOS = RAIZ / "05_resultados"
if not RESULTADOS.is_dir() and (RAIZ / "06_resultados").is_dir():
    RESULTADOS = RAIZ / "06_resultados"
TAMANOS = (500, 1000, 1500)
SEMILLA_BASE = 2026


def comprobar_resultados_previos():
    """Impide preparar entradas nuevas si ya existen mediciones."""
    for ruta in RESULTADOS.glob("*.csv"):
        with ruta.open(newline="", encoding="utf-8") as archivo:
            lector = csv.reader(archivo)
            next(lector, None)
            if any(fila for fila in lector):
                raise ValueError(
                    "Ya existen mediciones. Conserva la sesión completa antes "
                    "de preparar entradas para otra sesión."
                )


def guardar_o_comprobar(ruta, contenido):
    """Conserva los archivos existentes si coinciden con la semilla elegida."""
    if ruta.exists():
        if ruta.read_text(encoding="ascii") != contenido:
            raise ValueError(
                f"La entrada existente no coincide con la semilla: {ruta}. "
                "Respalda los datos antes de sustituirlos."
            )
        return

    with ruta.open("w", encoding="ascii", newline="\n") as archivo:
        archivo.write(contenido)


def principal():
    if sys.argv[1:]:
        raise ValueError('Uso: python ".\\03_crear matrices\\crear_matrices.py"')
    comprobar_resultados_previos()

    manifiesto = {
        "semilla_base": SEMILLA_BASE,
        "regla_semilla": "2026 + N",
        "generador": "random.Random; randrange(10); primero A y después B",
        "version_python_generador": sys.version,
        "tipo_datos_al_cargar": "punto flotante de doble precisión, 64 bits",
        "rango_entradas": [0, 9],
        "archivos": {},
    }

    for n in TAMANOS:
        carpeta = MATRICES / str(n)
        carpeta.mkdir(parents=True, exist_ok=True)
        generador = random.Random(SEMILLA_BASE + n)

        # Se genera una única pareja por tamaño, compartida por los lenguajes.
        a = [[generador.randrange(10) for _ in range(n)] for _ in range(n)]
        b = [[generador.randrange(10) for _ in range(n)] for _ in range(n)]

        for nombre, matriz in (("a.txt", a), ("b.txt", b)):
            contenido = f"{n}\n" + "".join(
                " ".join(map(str, fila)) + "\n" for fila in matriz
            )
            guardar_o_comprobar(carpeta / nombre, contenido)

        # sum(C) = sum_k(sum_i A[i,k] * sum_j B[k,j]).
        # Esta identidad obtiene una referencia sin calcular todo el producto.
        columnas_a = [sum(a[fila][k] for fila in range(n)) for k in range(n)]
        filas_b = [sum(b[k]) for k in range(n)]
        total = sum(columnas_a[k] * filas_b[k] for k in range(n))
        celdas = [
            sum(a[posicion][k] * b[k][posicion] for k in range(n))
            for posicion in (0, n // 2, n - 1)
        ]
        control = "\n".join(map(str, [n, total, *celdas])) + "\n"
        guardar_o_comprobar(carpeta / "control.txt", control)

        for nombre in ("a.txt", "b.txt", "control.txt"):
            manifiesto["archivos"][f"{n}/{nombre}"] = hashlib.sha256(
                (carpeta / nombre).read_bytes()
            ).hexdigest()

        print(f"Entradas listas: N={n}, semilla={SEMILLA_BASE + n}")

    (MATRICES / "manifiesto.json").write_text(
        json.dumps(manifiesto, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("Matrices y manifiesto preparados.")


if __name__ == "__main__":
    try:
        principal()
    except (OSError, ValueError) as error:
        sys.exit(f"Error: {error}")
