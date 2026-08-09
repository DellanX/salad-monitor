param(
    [string]$ExePath = "$PSScriptRoot\..\dist\salad-sidecar.exe",
    [string]$ServiceName = "SaladMonitorSidecar",
    [string]$DisplayName = "Salad Monitor Sidecar Service",
    [string]$NssmPath = "nssm.exe"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ExePath)) {
    throw "Executable not found at $ExePath"
}

if (-not (Get-Command $NssmPath -ErrorAction SilentlyContinue)) {
    throw "nssm.exe is required to install the service."
}

& $NssmPath install $ServiceName $ExePath
& $NssmPath set $ServiceName DisplayName $DisplayName
& $NssmPath set $ServiceName Start SERVICE_AUTO_START
& $NssmPath set $ServiceName AppStdout "$env:ProgramData\SaladMonitor\salad-sidecar.out.log"
& $NssmPath set $ServiceName AppStderr "$env:ProgramData\SaladMonitor\salad-sidecar.err.log"
& $NssmPath start $ServiceName
