<#
.SYNOPSIS
Guarda las versiones de los lenguajes o de Docker en un archivo TXT.

.DESCRIPTION
Consulta las herramientas incluidas en las imagenes existentes.
No construye imagenes ni ejecuta el experimento.
Los archivos se guardan en 02_caracteristicas_equipo, junto a este proyecto.
El archivo anterior se conserva si falla alguna consulta.

.EXAMPLE
.\capturar_versiones.ps1 -Tipo Lenguajes
Genera versiones_lenguajes.txt con C++, Go, Python, java y javac.

.EXAMPLE
.\capturar_versiones.ps1 -Tipo Docker
Genera docker_version.txt con las versiones del cliente y del servidor.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Lenguajes", "Docker")]
    [string]$Tipo
)

$ErrorActionPreference = "Stop"
$rutaRegistros = Join-Path $PSScriptRoot "02_caracteristicas_equipo"
if (-not (Test-Path -LiteralPath $rutaRegistros -PathType Container)) {
    throw "Falta la carpeta 02_caracteristicas_equipo del proyecto."
}

$comandoDocker = Get-Command docker.exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if ($comandoDocker) {
    $ejecutableDocker = $comandoDocker.Source
} else {
    $candidatos = @(
        (Join-Path $env:LOCALAPPDATA "Programs\DockerDesktop\resources\bin\docker.exe"),
        (Join-Path $env:USERPROFILE "AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe"),
        (Join-Path $env:ProgramFiles "Docker\Docker\resources\bin\docker.exe")
    )
    $ejecutableDocker = $candidatos | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
}
if (-not $ejecutableDocker) {
    throw "No se encontro Docker. Instala Docker Desktop y abre una nueva ventana de PowerShell."
}

function Invoke-DockerTexto {
    param([string[]]$Argumentos)

    # Los argumentos utilizados aqui son constantes y no contienen espacios.
    # ProcessStartInfo captura stdout y stderr como texto, tambien en PowerShell 5.1.
    $inicio = New-Object System.Diagnostics.ProcessStartInfo
    $inicio.FileName = $ejecutableDocker
    $inicio.Arguments = $Argumentos -join " "
    $inicio.WorkingDirectory = $PSScriptRoot
    $inicio.UseShellExecute = $false
    $inicio.CreateNoWindow = $true
    $inicio.RedirectStandardOutput = $true
    $inicio.RedirectStandardError = $true

    $proceso = New-Object System.Diagnostics.Process
    $proceso.StartInfo = $inicio
    try {
        $null = $proceso.Start()
        $salidaPendiente = $proceso.StandardOutput.ReadToEndAsync()
        $errorPendiente = $proceso.StandardError.ReadToEndAsync()

        if (-not $proceso.WaitForExit(60000)) {
            $proceso.Kill()
            $proceso.WaitForExit()
            throw "Docker no respondio en 60 segundos. Comprueba Docker Desktop."
        }

        $salida = $salidaPendiente.GetAwaiter().GetResult()
        $errores = $errorPendiente.GetAwaiter().GetResult()
        $partes = @($salida.TrimEnd(), $errores.TrimEnd()) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
        $texto = $partes -join [Environment]::NewLine

        if ($proceso.ExitCode -ne 0) {
            throw ("Fallo docker {0}: {1}" -f ($Argumentos -join " "), $texto)
        }
        if ([string]::IsNullOrWhiteSpace($texto)) {
            throw ("Docker no devolvio una version o respuesta: {0}" -f ($Argumentos -join " "))
        }
        return $texto
    } finally {
        $proceso.Dispose()
    }
}

$contenido = New-Object "System.Collections.Generic.List[string]"
$contenido.Add("Fecha de captura: " + (Get-Date -Format o))
$contenido.Add("")

if ($Tipo -eq "Lenguajes") {
    $consultas = @(
        @{Nombre="C++ (compilador g++)"; Imagen="matrices-cpp:semana3"; Programa="g++"; Version="--version"},
        @{Nombre="Go"; Imagen="matrices-go:semana3"; Programa="go"; Version="version"},
        @{Nombre="Python"; Imagen="matrices-python:semana3"; Programa="python"; Version="--version"},
        @{Nombre="Java (ejecucion)"; Imagen="matrices-java:semana3"; Programa="java"; Version="-version"},
        @{Nombre="Java (compilador javac)"; Imagen="matrices-java:semana3"; Programa="javac"; Version="-version"}
    )

    $imagenes = @("matrices-cpp:semana3", "matrices-go:semana3", "matrices-python:semana3", "matrices-java:semana3")
    $argumentosInspeccion = @("image", "inspect", "--format", "{{.Id}}") + $imagenes
    $null = Invoke-DockerTexto -Argumentos $argumentosInspeccion

    $contenido.Add("Versiones de las herramientas utilizadas dentro de los contenedores")
    $contenido.Add("")
    foreach ($consulta in $consultas) {
        $argumentosConsulta = @("run", "--rm", "--entrypoint", $consulta.Programa, $consulta.Imagen, $consulta.Version)
        $version = Invoke-DockerTexto -Argumentos $argumentosConsulta
        $contenido.Add("=== " + $consulta.Nombre + " ===")
        $contenido.Add("Imagen: " + $consulta.Imagen)
        $contenido.Add($version)
        $contenido.Add("")
    }
    $destino = Join-Path $rutaRegistros "versiones_lenguajes.txt"
} else {
    $version = Invoke-DockerTexto -Argumentos @("version")
    $contenido.Add("Version de Docker: cliente y servidor")
    $contenido.Add("")
    $contenido.Add($version)
    $destino = Join-Path $rutaRegistros "docker_version.txt"
}

# Se escribe despues de completar todas las consultas correctamente.
$textoFinal = ($contenido -join [Environment]::NewLine) + [Environment]::NewLine
[IO.File]::WriteAllText($destino, $textoFinal, [Text.UTF8Encoding]::new($false))
Write-Host ("Versiones guardadas en: {0}" -f $destino)

