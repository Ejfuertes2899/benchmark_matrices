from pathlib import Path
import numpy as np
import pandas as pd


columnas = ["language", "N", "repetition", "time_seconds"]

tablas = []

for ruta in snakemake.input:
    tabla = pd.read_csv(
        ruta,
        dtype={
            "language": str,
            "N": int,
            "repetition": int,
            "time_seconds": float,
        },
    )

    if list(tabla.columns) != columnas:
        raise ValueError(f"Columnas incorrectas en {ruta}")

    tablas.append(tabla)

datos = pd.concat(tablas, ignore_index=True)

esperados = {
    (lenguaje, n, repeticion)
    for lenguaje in ["cpp", "go", "java", "python"]
    for n in [500, 1000, 1500]
    for repeticion in range(1, 11)
}

encontrados = list(
    datos[["language", "N", "repetition"]]
    .itertuples(index=False, name=None)
)

if len(encontrados) != 120 or set(encontrados) != esperados:
    raise ValueError(
        "Se requieren exactamente las 120 combinaciones, "
        "sin mediciones faltantes ni duplicadas."
    )

tiempos = datos["time_seconds"].to_numpy()

if not np.isfinite(tiempos).all() or (tiempos <= 0).any():
    raise ValueError("Los tiempos deben ser finitos y positivos.")

datos = datos.sort_values(
    ["language", "N", "repetition"]
).reset_index(drop=True)

salida = Path(snakemake.output[0])
salida.parent.mkdir(parents=True, exist_ok=True)
datos.to_csv(salida, index=False)

print("benchmark.csv generado: 120 filas.")
