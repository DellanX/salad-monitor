param(
    [string]$ExePath = "$PSScriptRoot\..\dist\salad-monitor.exe",
    [string]$ServiceName = "SaladMonitor",
    [string]$DisplayName = "Salad Monitor Service",
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
& $NssmPath set $ServiceName AppStdout "$env:ProgramData\SaladMonitor\salad-monitor.out.log"
& $NssmPath set $ServiceName AppStderr "$env:ProgramData\SaladMonitor\salad-monitor.err.log"
& $NssmPath start $ServiceName
