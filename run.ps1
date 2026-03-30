$pythonVenv = Join-Path $PSScriptRoot ".venv/Scripts/python.exe"
$pythonParentVenv = Join-Path $PSScriptRoot "../.venv/Scripts/python.exe"
$mainFile = Join-Path $PSScriptRoot "src/main/python/org/example/main.py"

if (Test-Path $pythonVenv) {
	& $pythonVenv $mainFile
} elseif (Test-Path $pythonParentVenv) {
	& $pythonParentVenv $mainFile
} else {
	$pyCmd = Get-Command py -ErrorAction SilentlyContinue
	if ($pyCmd) {
		py -3 $mainFile
		exit $LASTEXITCODE
	}

	$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
	if (-not $pythonCmd) {
		Write-Host "No se encontro Python en el sistema."
		Write-Host "Instala Python 3.10+ o usa el lanzador py."
		exit 1
	}

	python --version *> $null
	if ($LASTEXITCODE -ne 0) {
		Write-Host "Se detecto el alias de Python, pero no hay un interprete funcional instalado."
		Write-Host "Instala Python 3.10+ o usa el lanzador py."
		exit 1
	}

	python $mainFile
}
