[CmdletBinding()]
param(
    [int]$Semilla = 2027,
    [switch]$SoloOrden
)

$ErrorActionPreference = "Stop"
$raiz = $PSScriptRoot
$rutaResultados = Join-Path $raiz "05_resultados"
$rutaRegistros = Join-Path $raiz "02_caracteristicas_equipo"

if (-not (Test-Path -LiteralPath $rutaResultados -PathType Container)) {
    throw "Falta la carpeta 05_resultados del proyecto."
}
if (-not (Test-Path -LiteralPath $rutaRegistros -PathType Container)) {
    throw "Falta la carpeta 02_caracteristicas_equipo del proyecto."
}
if (-not $SoloOrden) {
    $existentes = @(Get-ChildItem -LiteralPath $rutaResultados -File -Filter "*.csv")
    if ($existentes.Count -gt 0) {
        throw "05_resultados ya contiene archivos CSV. Conserva esos CSV en otra ubicacion antes de iniciar una nueva sesion. No se modifico ningun resultado."
    }
}
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "No se encontro Docker. Abre Docker Desktop y una nueva ventana de PowerShell."
}

$tipoSistema = @(& docker info --format "{{.OSType}}")
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo consultar Docker. Comprueba que Docker Desktop este funcionando."
}
if (($tipoSistema -join "").Trim() -ne "linux") {
    throw "Este proyecto necesita que Docker utilice contenedores Linux."
}

$imagenes = @(
    "matrices-cpp:semana3",
    "matrices-go:semana3",
    "matrices-java:semana3",
    "matrices-python:semana3"
)
& docker image inspect @imagenes > $null
if ($LASTEXITCODE -ne 0) {
    throw "Falta alguna imagen del experimento. Construye las cuatro imagenes manualmente siguiendo el README."
}

# Se conserva el generador de Python y el orden inicial de la semana 2.
$codigoOrden = @'
import random
import sys

bloques = [
    f'{lenguaje},{n}'
    for lenguaje in ('cpp', 'go', 'java', 'python')
    for n in (500, 1000, 1500)
]
random.Random(int(sys.argv[1])).shuffle(bloques)
print('\n'.join(bloques))
'@

$salidaOrden = @(& docker run --rm --entrypoint python matrices-python:semana3 -c $codigoOrden ([string]$Semilla))
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo generar el orden aleatorizado. No se iniciaron las mediciones."
}
$orden = @($salidaOrden | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$esperados = @(
    foreach ($lenguaje in @("cpp", "go", "java", "python")) {
        foreach ($tamano in @(500, 1000, 1500)) {
            "$lenguaje,$tamano"
        }
    }
)
if ($orden.Count -ne 12) {
    throw "El orden generado debe contener doce bloques."
}
if (@(Compare-Object -ReferenceObject $esperados -DifferenceObject $orden).Count -ne 0) {
    throw "El orden generado no contiene exactamente las doce combinaciones esperadas."
}

$plan = @(
    for ($indice = 0; $indice -lt $orden.Count; $indice++) {
        $lenguaje, $tamano = $orden[$indice].Split(",")
        [pscustomobject]@{
            bloque = $indice + 1
            language = $lenguaje
            N = [int]$tamano
            seed = $Semilla
        }
    }
)

Write-Host ("Semilla del orden: {0}" -f $Semilla)
$plan | Format-Table bloque, language, N -AutoSize | Out-Host

if ($SoloOrden) {
    Write-Host "Consulta terminada: no se ejecutaron mediciones ni se escribieron archivos."
    return
}

$nombreOrden = "orden_ejecucion_semilla_{0}_{1}.csv" -f $Semilla, (Get-Date -Format "yyyyMMdd_HHmmss")
$rutaOrden = Join-Path $rutaRegistros $nombreOrden
$plan | Export-Csv -LiteralPath $rutaOrden -NoTypeInformation -Encoding UTF8 -NoClobber

# El nombre en Windows cambia; la ruta interna conserva las imagenes existentes.
$montaje = "type=bind,source=$rutaResultados,target=/app/06_resultados"
foreach ($bloque in $plan) {
    Write-Host ("Bloque {0}/12: {1}, N={2}" -f $bloque.bloque, $bloque.language, $bloque.N)
    $imagen = "matrices-{0}:semana3" -f $bloque.language
    & docker run --rm --cpus=1 --mount $montaje $imagen ([string]$bloque.N)

    if ($LASTEXITCODE -ne 0) {
        throw ("Fallo el bloque {0}/12: {1}, N={2}. Se detuvo la sesion y se conservaron los resultados parciales en 05_resultados." -f $bloque.bloque, $bloque.language, $bloque.N)
    }
}

# El verificador ya existe en las imagenes construidas.
$montajeLectura = $montaje + ",readonly"
& docker run --rm --mount $montajeLectura --entrypoint python matrices-python:semana3 "07_revisión de archivos/revisar_archivos.py" --completo
if ($LASTEXITCODE -ne 0) {
    throw "Los contenedores terminaron, pero los resultados no pasaron la verificacion final. Se conservaron los CSV."
}

Write-Host "Experimento completo: 120 mediciones validas."
Write-Host ("Resultados: {0}" -f $rutaResultados)
Write-Host ("Semilla y orden planificado: {0}" -f $rutaOrden)

