from pathlib import Path
import csv
import hashlib
import importlib.util
import json
import random
import shutil
import subprocess
import tempfile


raiz = Path.cwd().resolve()
lenguajes = ["cpp", "go", "java", "python"]
tamanos = [500, 1000, 1500]
semilla = int(snakemake.params.semilla)

destino = Path(snakemake.output.csvs[0]).parent
destino.mkdir(parents=True, exist_ok=True)

tipo = subprocess.check_output(
    ["docker", "info", "--format", "{{.OSType}}"],
    text=True,
).strip()

if tipo != "linux":
    raise RuntimeError("Docker debe utilizar contenedores Linux.")

# Cargar el verificador que ya existe en el proyecto.
especificacion = importlib.util.spec_from_file_location(
    "verificador",
    str(snakemake.input.verificador),
)
verificador = importlib.util.module_from_spec(especificacion)
especificacion.loader.exec_module(verificador)
verificador.revisar_matrices()

etiquetas = [
    f"matrices-{lenguaje}:semana4"
    for lenguaje in lenguajes
]

inspecciones = json.loads(
    subprocess.check_output(
        ["docker", "image", "inspect", *etiquetas],
        text=True,
    )
)

imagenes = {
    lenguaje: {
        "etiqueta": etiqueta,
        "id": informacion["Id"],
        "creada": informacion["Created"],
    }
    for lenguaje, etiqueta, informacion
    in zip(lenguajes, etiquetas, inspecciones)
}

# Detectar imágenes antiguas frente a archivos locales modificados.
comunes = [
    *map(str, snakemake.input.matrices),
    str(snakemake.input.manifiesto),
]

for lenguaje, fuente in zip(lenguajes, snakemake.input.fuentes):
    archivos = [str(fuente), *comunes]

    esperados = [
        hashlib.sha256((raiz / archivo).read_bytes()).hexdigest()
        for archivo in archivos
    ]

    respuesta = subprocess.check_output(
        [
            "docker", "run", "--rm", "--pull=never",
            "--entrypoint", "sha256sum",
            imagenes[lenguaje]["id"],
            *[f"/app/{archivo}" for archivo in archivos],
        ],
        text=True,
    )

    encontrados = [
        linea.split()[0]
        for linea in respuesta.splitlines()
    ]

    if encontrados != esperados:
        raise RuntimeError(
            f"La imagen de {lenguaje} no coincide con el artifact. "
            "Reconstruye manualmente las cuatro imágenes."
        )

# Registrar el entorno de esta misma sesión antes de iniciar las mediciones.
especificacion_equipo = importlib.util.spec_from_file_location(
    "registrar_equipo",
    str(snakemake.input.registro_equipo),
)
registrador = importlib.util.module_from_spec(especificacion_equipo)
especificacion_equipo.loader.exec_module(registrador)
registros = registrador.recopilar_registros(
    imagenes, semilla, snakemake.input.entorno,
)
for ruta in snakemake.output.registros_equipo:
    archivo = Path(ruta)
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(registros[archivo.name], encoding="utf-8")
print("Equipo y versiones registrados automáticamente.", flush=True)

orden = [
    (lenguaje, n)
    for lenguaje in lenguajes
    for n in tamanos
]
random.Random(semilla).shuffle(orden)

# Cada intento comienza con un directorio de mediciones vacío.
with tempfile.TemporaryDirectory(
    prefix=".corrida-",
    dir=destino,
) as temporal:

    carpeta_temporal = Path(temporal).resolve()

    with Path(snakemake.log[0]).open(
        "w", encoding="utf-8"
    ) as registro:

        registro.write(f"Semilla: {semilla}\n")
        registro.flush()

        for bloque, (lenguaje, n) in enumerate(orden, start=1):
            mensaje = f"Bloque {bloque}/12: {lenguaje}, N={n}"
            print(mensaje, flush=True)
            registro.write(mensaje + "\n")
            registro.flush()

            comando = [
                "docker", "run",
                "--rm",
                "--pull=never",
                "--cpus=1",
                "--mount",
                (
                    f"type=bind,source={carpeta_temporal},"
                    "target=/app/06_resultados"
                ),
                imagenes[lenguaje]["id"],
                str(n),
            ]

            with subprocess.Popen(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            ) as proceso:
                for linea in proceso.stdout:
                    print(linea, end="", flush=True)
                    registro.write(linea)
                    registro.flush()

                if proceso.wait() != 0:
                    raise RuntimeError(
                        f"Falló el bloque: {lenguaje}, N={n}. "
                        "Consulta ejecucion.log."
                    )

    # Exigir las 120 mediciones y ordenar los CSV.
    verificador.RESULTADOS = carpeta_temporal
    verificador.exigir_completo(verificador.leer_resultados())
    verificador.ordenar_resultados()

    for lenguaje, salida in zip(
        lenguajes, snakemake.output.csvs
    ):
        shutil.copyfile(
            carpeta_temporal / f"{lenguaje}.csv",
            salida,
        )

with Path(snakemake.output.orden).open(
    "w", newline="", encoding="utf-8"
) as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow(["bloque", "language", "N", "seed"])
    escritor.writerows(
        (bloque, lenguaje, n, semilla)
        for bloque, (lenguaje, n)
        in enumerate(orden, start=1)
    )

Path(snakemake.output.imagenes).write_text(
    json.dumps(imagenes, indent=2) + "\n",
    encoding="utf-8",
)

print("Experimento terminado: 120 mediciones verificadas.")
