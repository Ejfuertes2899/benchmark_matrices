LENGUAJES = ["cpp", "go", "java", "python"]
TAMANOS = [500, 1000, 1500]

RESULTADOS = "05_resultados"
ANALISIS = "08_analisis"

CARACTERISTICAS = "02_caracteristicas_equipo"
REGISTROS_EQUIPO = [
    CARACTERISTICAS + "/" + nombre
    for nombre in [
        "caracteristicas_equipo.txt",
        "versiones_lenguajes.txt",
        "python_workflow.txt",
        "snakemake_version.txt",
        "docker_version.txt",
        "imagenes.json",
    ]
]

CSV_INDIVIDUALES = expand(
    RESULTADOS + "/{lenguaje}.csv",
    lenguaje=LENGUAJES,
)

PRODUCTOS_ANALISIS = [
    ANALISIS + "/descriptivos.csv",
    ANALISIS + "/anova.csv",
    ANALISIS + "/anova_log.csv",
    ANALISIS + "/supuestos.csv",
    ANALISIS + "/tukey.csv",
    ANALISIS + "/resumen.txt",
    ANALISIS + "/cajas.png",
    ANALISIS + "/interaccion.png",
    ANALISIS + "/diagnostico.png",
]


rule all:
    input:
        CSV_INDIVIDUALES,
        RESULTADOS + "/orden.csv",
        RESULTADOS + "/imagenes.json",
        RESULTADOS + "/benchmark.csv",
        PRODUCTOS_ANALISIS,
        REGISTROS_EQUIPO,


rule ejecutar_contenedores:
    input:
        fuentes=[
            "04_programas_matrices/matrices.cpp",
            "04_programas_matrices/matrices.go",
            "04_programas_matrices/Matrices.java",
            "04_programas_matrices/matrices.py",
        ],
        dockerfiles=expand(
            "01_docker/{lenguaje}/Dockerfile",
            lenguaje=LENGUAJES,
        ),
        matrices=expand(
            "03_crear matrices/{n}/{archivo}",
            n=TAMANOS,
            archivo=["a.txt", "b.txt", "control.txt"],
        ),
        manifiesto="03_crear matrices/manifiesto.json",
        verificador="06_revisión de archivos/revisar_archivos.py",
        entorno="requirements.txt",
        registro_equipo="07_workflow/registrar_equipo.py",
    output:
        csvs=CSV_INDIVIDUALES,
        orden=RESULTADOS + "/orden.csv",
        imagenes=RESULTADOS + "/imagenes.json",
        registros_equipo=REGISTROS_EQUIPO,
    params:
        semilla=2027,
    log:
        RESULTADOS + "/ejecucion.log",
    script:
        "07_workflow/ejecutar.py"


rule integrar:
    input:
        CSV_INDIVIDUALES,
    output:
        RESULTADOS + "/benchmark.csv",
    script:
        "07_workflow/integrar.py"


rule analizar:
    input:
        RESULTADOS + "/benchmark.csv",
    output:
        PRODUCTOS_ANALISIS,
    params:
        alpha=0.05,
    script:
        "07_workflow/analizar.py"
