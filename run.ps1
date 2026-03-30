$pythonVenv = Join-Path $PSScriptRoot ".venv/Scripts/python.exe"
$mainFile = Join-Path $PSScriptRoot "src/main/python/org/example/main.py"

if (Test-Path $pythonVenv) {
	& $pythonVenv $mainFile
} else {
	$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
	if (-not $pythonCmd) {
		Write-Host "No se encontro Python en el sistema."
		Write-Host "Instala Python 3.10+ o crea un entorno .venv en esta carpeta."
		exit 1
	}

	python --version *> $null
	if ($LASTEXITCODE -ne 0) {
		Write-Host "Se detecto el alias de Python, pero no hay un interprete funcional instalado."
		Write-Host "Instala Python 3.10+ o crea un entorno .venv en esta carpeta."
		exit 1
	}

	python $mainFile
}
