param(
    [string]$Version = "0.2.0"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    throw "pyinstaller is required. Install with: pip install -r requirements-build.txt"
}

$normalizedVersion = $Version.Trim()
if ($normalizedVersion.StartsWith("v")) {
    $normalizedVersion = $normalizedVersion.Substring(1)
}

$versionParts = $normalizedVersion.Split(".")
$major = if ($versionParts.Count -ge 1 -and $versionParts[0]) { [int]$versionParts[0] } else { 0 }
$minor = if ($versionParts.Count -ge 2 -and $versionParts[1]) { [int]$versionParts[1] } else { 0 }
$patch = if ($versionParts.Count -ge 3 -and $versionParts[2]) { [int]$versionParts[2] } else { 0 }

$versionFile = Join-Path $PSScriptRoot "pyinstaller-version-info.txt"
@"
# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=($major, $minor, $patch, 0),
    prodvers=($major, $minor, $patch, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', 'DellanX'),
        StringStruct('FileDescription', 'Salad Monitor'),
        StringStruct('FileVersion', '$normalizedVersion'),
        StringStruct('InternalName', 'salad-monitor'),
        StringStruct('OriginalFilename', 'salad-monitor.exe'),
        StringStruct('ProductName', 'Salad Monitor'),
        StringStruct('ProductVersion', '$normalizedVersion')])
      ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"@ | Set-Content -Path $versionFile -Encoding UTF8

Push-Location (Join-Path $PSScriptRoot "..")
try {
    pyinstaller --noconfirm --clean --onefile --name salad-monitor --version-file $versionFile salad_monitor.py
    pyinstaller --noconfirm --clean --onefile --name salad-sidecar --version-file $versionFile salad_sidecar.py
} finally {
    Pop-Location
    if (Test-Path $versionFile) {
        Remove-Item $versionFile -Force
    }
}

Write-Host "Built executables:"
Write-Host "  dist\salad-monitor.exe"
Write-Host "  dist\salad-sidecar.exe"
