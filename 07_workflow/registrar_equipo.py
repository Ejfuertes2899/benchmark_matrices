"""Recopila el equipo y las versiones utilizadas antes de medir.

Este módulo se invoca desde ejecutar.py; no realiza multiplicaciones ni
construye imágenes. Solo utiliza la biblioteca estándar de Python.
"""

from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
import base64
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys


def consultar(comando, timeout=60):
    """Consulta una herramienta y falla si no devuelve una respuesta válida."""
    try:
        respuesta = subprocess.run(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env={**os.environ, "LC_ALL": "C", "LANG": "C"},
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError(
            f"No se pudo consultar {comando[0]}: {error}"
        ) from error
    texto = respuesta.stdout.strip()
    if respuesta.returncode != 0 or not texto:
        raise RuntimeError(
            f"Falló la consulta {' '.join(comando)}: {texto}"
        )
    return texto


def gib(valor):
    """Expresa una cantidad de bytes en GiB sin confundirla con GB."""
    if valor is None:
        return "No disponible"
    return f"{int(valor) / (1024 ** 3):.2f} GiB ({int(valor)} bytes)"


def datos_windows():
    """Consulta el equipo anfitrión; su ausencia no impide ejecutar en Linux."""
    if "microsoft" not in platform.release().lower():
        return None, "No aplica: este entorno no se identifica como WSL."

    powershell = shutil.which("powershell.exe")
    if powershell is None:
        return None, (
            "No disponible: la interoperabilidad con PowerShell no está "
            "habilitada. Los datos de Ubuntu/WSL y Docker sí se registran."
        )

    consulta = r"""
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$taskOs = Get-CimInstance -ClassName Win32_OperatingSystem
$taskMachine = Get-CimInstance -ClassName Win32_ComputerSystem
$taskProcessors = @(Get-CimInstance -ClassName Win32_Processor)
[ordered]@{
    sistema = $taskOs.Caption
    version = $taskOs.Version
    compilacion = $taskOs.BuildNumber
    fabricante = $taskMachine.Manufacturer
    modelo = $taskMachine.Model
    ram_fisica_bytes = [int64]$taskMachine.TotalPhysicalMemory
    procesadores = @($taskProcessors | ForEach-Object {
        [ordered]@{
            nombre = $_.Name
            nucleos_fisicos = $_.NumberOfCores
            procesadores_logicos = $_.NumberOfLogicalProcessors
        }
    })
} | ConvertTo-Json -Depth 5 -Compress
"""
    codificada = base64.b64encode(
        consulta.encode("utf-16-le")
    ).decode("ascii")
    try:
        respuesta = consultar(
            [
                powershell, "-NoLogo", "-NoProfile", "-NonInteractive",
                "-EncodedCommand", codificada,
            ],
            timeout=30,
        )
        return json.loads(respuesta.lstrip("\ufeff")), None
    except (RuntimeError, ValueError) as error:
        return None, f"No disponible: {error}"


def recopilar_registros(imagenes, semilla, requisitos):
    """Devuelve los seis registros de una misma captura del entorno."""
    fecha = datetime.now(timezone.utc).isoformat(timespec="seconds")
    encabezado = f"Fecha de captura (UTC): {fecha}\n\n"
    requisitos = Path(requisitos)
    docker_info = json.loads(
        consultar(["docker", "info", "--format", "{{json .}}"])
    )
    docker_version = consultar(["docker", "version"])
    snakemake_version = metadata.version("snakemake")

    consultas = [
        ("C++ (compilador g++)", "cpp", "g++", ["--version"]),
        ("Go", "go", "go", ["version"]),
        ("Python del contenedor", "python", "python", ["--version"]),
        ("Java (ejecución)", "java", "java", ["-version"]),
        ("Java (compilador javac)", "java", "javac", ["-version"]),
    ]
    versiones_lenguajes = []
    for nombre, lenguaje, programa, argumentos in consultas:
        imagen = imagenes[lenguaje]
        version = consultar([
            "docker", "run", "--rm", "--pull=never",
            "--entrypoint", programa, imagen["id"], *argumentos,
        ])
        versiones_lenguajes.extend([
            nombre,
            f"Imagen: {imagen['etiqueta']}",
            f"Identificador: {imagen['id']}",
            version,
            "",
        ])

    distribucion = platform.freedesktop_os_release().get(
        "PRETTY_NAME", platform.system()
    )
    cpu = platform.processor() or "No disponible"
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.is_file():
        for linea in cpuinfo.read_text(encoding="utf-8").splitlines():
            if linea.startswith("model name"):
                cpu = linea.split(":", 1)[1].strip()
                break

    memoria_wsl = (
        os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    )
    cpu_permitidas = (
        len(os.sched_getaffinity(0))
        if hasattr(os, "sched_getaffinity") else os.cpu_count()
    )
    anfitrion, motivo_windows = datos_windows()
    lineas = [
        encabezado.rstrip(),
        "",
        "EQUIPO Y SISTEMA DEL WORKFLOW",
        f"Nombre del equipo en Linux: {platform.node()}",
        f"Sistema: {distribucion}",
        f"Kernel: {platform.release()}",
        f"Arquitectura: {platform.machine()}",
        f"CPU visible en Ubuntu/WSL: {cpu}",
        f"Procesadores lógicos visibles en Ubuntu/WSL: {os.cpu_count()}",
        f"Procesadores permitidos al proceso: {cpu_permitidas}",
        f"RAM visible en Ubuntu/WSL: {gib(memoria_wsl)}",
        "",
        "EQUIPO WINDOWS ANFITRIÓN",
    ]
    if anfitrion is None:
        lineas.append(motivo_windows)
    else:
        lineas.extend([
            f"Sistema: {anfitrion['sistema']}",
            f"Versión: {anfitrion['version']}",
            f"Compilación: {anfitrion['compilacion']}",
            f"Fabricante: {anfitrion['fabricante']}",
            f"Modelo: {anfitrion['modelo']}",
            f"RAM física informada por Windows: {gib(anfitrion['ram_fisica_bytes'])}",
        ])
        for indice, procesador in enumerate(
            anfitrion["procesadores"], start=1
        ):
            lineas.extend([
                f"Procesador {indice}: {procesador['nombre']}",
                f"Núcleos físicos: {procesador['nucleos_fisicos']}",
                "Procesadores lógicos: "
                f"{procesador['procesadores_logicos']}",
            ])

    lineas.extend([
        "",
        "RECURSOS DEL MOTOR DOCKER",
        f"Nombre del servidor: {docker_info.get('Name')}",
        f"Sistema del servidor: {docker_info.get('OperatingSystem')}",
        f"Kernel del servidor: {docker_info.get('KernelVersion')}",
        f"Arquitectura: {docker_info.get('Architecture')}",
        f"Versión del servidor: {docker_info.get('ServerVersion')}",
        f"Procesadores lógicos disponibles: {docker_info.get('NCPU')}",
        f"RAM disponible: {gib(docker_info.get('MemTotal'))}",
        "",
        "CONFIGURACIÓN DEL EXPERIMENTO",
        "Lenguajes: cpp, go, java, python",
        "Tamaños N: 500, 1000, 1500",
        "Repeticiones medidas por combinación: 10",
        "Calentamientos excluidos por combinación: 2",
        f"Semilla del orden de los bloques: {semilla}",
        "Límite de CPU por contenedor: --cpus=1",
        "Ejecución de bloques: secuencial",
        "",
        "ENTORNO PYTHON DEL WORKFLOW",
        f"Python: {sys.version.replace(chr(10), ' ')}",
        f"Ejecutable: {sys.executable}",
        f"Snakemake: {snakemake_version}",
        f"Archivo de dependencias: {requisitos}",
        "SHA-256 de requirements.txt: "
        + hashlib.sha256(requisitos.read_bytes()).hexdigest(),
    ])
    for paquete in ["numpy", "pandas", "scipy", "statsmodels", "matplotlib"]:
        lineas.append(f"{paquete}: {metadata.version(paquete)}")
    lineas.extend([
        "",
        "La RAM física de Windows y la RAM visible en WSL/Docker "
        "son cantidades distintas.",
        "La cuota --cpus=1 no fija la ejecución a un núcleo físico concreto.",
        "Esta captura se realiza antes de los calentamientos y mediciones.",
    ])

    docker_texto = encabezado + docker_version + "\n"
    return {
        "caracteristicas_equipo.txt": "\n".join(lineas) + "\n",
        "versiones_lenguajes.txt": (
            encabezado + "\n".join(versiones_lenguajes).rstrip() + "\n"
        ),
        "python_workflow.txt": (
            encabezado + f"Python {sys.version}\n"
            + f"Ejecutable: {sys.executable}\n"
        ),
        "snakemake_version.txt": (
            encabezado + f"Snakemake {snakemake_version}\n"
        ),
        "docker_version.txt": docker_texto,
        "imagenes.json": json.dumps(
            {"fecha_captura_utc": fecha, "imagenes": imagenes},
            ensure_ascii=False, indent=2,
        ) + "\n",
    }
