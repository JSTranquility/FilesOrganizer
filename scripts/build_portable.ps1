param(
    [string]$Version = "1.1.0",
    [string]$PythonPath = ""
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if ($PythonPath) {
    $Python = $PythonPath
}
elseif (Test-Path $VenvPython) {
    $Python = $VenvPython
}
else {
    $Python = "python"
}

Push-Location $ProjectRoot
try {
    & $Python -m PyInstaller `
        --clean `
        --noconfirm `
        --onedir `
        --windowed `
        --noupx `
        --icon="assets\icon.ico" `
        --add-data="assets\icon.ico;assets" `
        --name="File Organizer" `
        "src\main.py"

    $ZipPath = "dist\File.Organizer.v$Version.Portable.zip"
    if (Test-Path $ZipPath) {
        Remove-Item $ZipPath -Force
    }

    Compress-Archive `
        -Path "dist\File Organizer\*" `
        -DestinationPath $ZipPath `
        -CompressionLevel Optimal

    Write-Host "Portable build created: $ZipPath"
}
finally {
    Pop-Location
}
