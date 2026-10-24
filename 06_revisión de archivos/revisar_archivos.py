"""Valida las entradas y los resultados, y ordena los CSV al finalizar."""

from pathlib import Path
from tempfile import NamedTemporaryFile
import csv
import hashlib
import json
import math
import sys

RAIZ = Path(__file__).resolve().parents[1]
MATRICES = RAIZ / "03_crear matrices"
# En el proyecto se usa 05; las imagenes Docker conservan su ruta interna.
RESULTADOS = RAIZ / "05_resultados"
if not RESULTADOS.is_dir() and (RAIZ / "06_resultados").is_dir():
    RESULTADOS = RAIZ / "06_resultados"

COLUMNAS = ["language", "N", "repetition", "time_seconds"]
LENGUAJES = ("cpp", "go", "java", "python")
TAMANOS = (500, 1000, 1500)
REPETICIONES = 10
CALENTAMIENTOS = 2


def revisar_matrices():
    """Verifica que estén las nueve entradas y que sus huellas no cambiaron."""
    ruta = MATRICES / "manifiesto.json"
    if not ruta.is_file():
        raise ValueError(
            'Falta el manifiesto. Primero ejecuta '
            'python ".\\03_crear matrices\\crear_matrices.py".'
        )

    manifiesto = json.loads(ruta.read_text(encoding="utf-8"))
    esperados = {
        f"{n}/{nombre}"
        for n in TAMANOS
        for nombre in ("a.txt", "b.txt", "control.txt")
    }
    if set(manifiesto["archivos"]) != esperados:
        raise ValueError("El manifiesto debe registrar las nueve entradas.")

    for nombre, esperado in manifiesto["archivos"].items():
        actual = hashlib.sha256((MATRICES / nombre).read_bytes()).hexdigest()
        if actual != esperado:
            raise ValueError(
                f"Cambió la entrada {nombre}. Recupera las entradas de la sesión."
            )


def leer_resultados():
    """Valida las filas existentes y devuelve las repeticiones por combinación."""
    grupos = {
        (lenguaje, n): set()
        for lenguaje in LENGUAJES
        for n in TAMANOS
    }
    for lenguaje in LENGUAJES:
        ruta = RESULTADOS / f"{lenguaje}.csv"
        if not ruta.exists() or ruta.stat().st_size == 0:
            continue

        with ruta.open(newline="", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            if lector.fieldnames != COLUMNAS:
                raise ValueError(f"Encabezado incorrecto en {ruta.name}.")

            for numero_fila, fila in enumerate(lector, start=2):
                ubicacion = f"{ruta.name}, fila {numero_fila}"
                if None in fila or any(valor is None for valor in fila.values()):
                    raise ValueError(f"Cantidad de columnas incorrecta: {ubicacion}.")

                n = int(fila["N"])
                repeticion = int(fila["repetition"])
                segundos = float(fila["time_seconds"])
                if (
                    fila["language"] != lenguaje
                    or n not in TAMANOS
                    or repeticion not in range(1, REPETICIONES + 1)
                ):
                    raise ValueError(f"Combinación inválida: {ubicacion}.")
                if not math.isfinite(segundos) or segundos <= 0:
                    raise ValueError(f"Tiempo inválido: {ubicacion}.")
                if repeticion in grupos[(lenguaje, n)]:
                    raise ValueError(f"Repetición duplicada: {ubicacion}.")

                grupos[(lenguaje, n)].add(repeticion)

    return grupos


def exigir_completo(grupos):
    """Exige las diez mediciones de cada una de las doce combinaciones."""
    pendientes = [
        f"{lenguaje}, N={n}: {len(repeticiones)}/{REPETICIONES}"
        for (lenguaje, n), repeticiones in grupos.items()
        if len(repeticiones) != REPETICIONES
    ]
    if pendientes:
        raise ValueError("Faltan mediciones: " + "; ".join(pendientes))


def ordenar_resultados():
    """Ordena los cuatro CSV completos por N y repetición, sin cambiar sus datos."""
    exigir_completo(leer_resultados())

    for lenguaje in LENGUAJES:
        destino = RESULTADOS / f"{lenguaje}.csv"
        with destino.open(newline="", encoding="utf-8") as archivo:
            filas = list(csv.DictReader(archivo))
        filas.sort(key=lambda fila: (int(fila["N"]), int(fila["repetition"])))

        temporal = None
        try:
            # Se conserva el CSV anterior hasta completar la escritura del nuevo.
            with NamedTemporaryFile(
                mode="w", newline="", encoding="utf-8",
                dir=RESULTADOS, prefix=f".{lenguaje}-",
                suffix=".csv.tmp", delete=False,
            ) as archivo:
                temporal = Path(archivo.name)
                escritor = csv.DictWriter(
                    archivo, fieldnames=COLUMNAS, lineterminator="\n",
                )
                escritor.writeheader()
                escritor.writerows(filas)
            temporal.replace(destino)
        finally:
            if temporal is not None:
                temporal.unlink(missing_ok=True)


def principal():
    if sys.argv[1:] not in ([], ["--completo"]):
        raise ValueError(
            'Uso: python ".\\06_revisión de archivos\\revisar_archivos.py" '
            "[--completo]"
        )

    revisar_matrices()
    grupos = leer_resultados()
    for (lenguaje, n), repeticiones in grupos.items():
        print(f"{lenguaje:6s} | N={n:4d} | {len(repeticiones)}/10 mediciones")

    total = sum(len(repeticiones) for repeticiones in grupos.values())
    print(f"Total: {total}/120 mediciones válidas.")
    if "--completo" in sys.argv:
        exigir_completo(grupos)


if __name__ == "__main__":
    try:
        principal()
    except (OSError, ValueError, KeyError, TypeError) as error:
        sys.exit(f"Error: {error}")
