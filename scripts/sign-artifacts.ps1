param(
    [string]$CertificateThumbprint,
    [string]$TimestampUrl = "http://timestamp.digicert.com",
    [string]$ArtifactsPath = "$PSScriptRoot\..\dist\*.exe"
)

$ErrorActionPreference = "Stop"

if (-not $CertificateThumbprint) {
    throw "CertificateThumbprint is required."
}

$signtool = Join-Path ${env:ProgramFiles(x86)} "Windows Kits\10\bin\x64\signtool.exe"
if (-not (Test-Path $signtool)) {
    throw "signtool.exe not found. Install Windows SDK."
}

$files = Get-ChildItem $ArtifactsPath -File
if ($files.Count -eq 0) {
    throw "No artifacts found to sign at $ArtifactsPath"
}

foreach ($file in $files) {
    & $signtool sign /sha1 $CertificateThumbprint /fd SHA256 /tr $TimestampUrl /td SHA256 $file.FullName
}
