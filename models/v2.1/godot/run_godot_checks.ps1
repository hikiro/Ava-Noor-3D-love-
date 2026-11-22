# Villa Verse v1.9 Godot 4 headless import check (Windows PowerShell 5.1+)
# Usage: powershell -ExecutionPolicy Bypass -File .\run_godot_checks.ps1 -GodotExe 'C:\\Tools\\Godot_v4.5-stable_win64_console.exe'
param([string]$GodotExe='godot')
$ErrorActionPreference='Stop'
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir=Join-Path $Root 'qa_engine_logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$ImportLog=Join-Path $LogDir 'godot_import.log'
$AuditLog=Join-Path $LogDir 'godot_validate.log'
try {
    $cmd=Get-Command $GodotExe -ErrorAction Stop
} catch {
    Write-Error "Godot binary not found: $GodotExe. Install Godot 4.x first, then pass -GodotExe with its full path."
    exit 127
}
& $GodotExe --headless --editor --path $Root --import *>&1 | Out-File -Encoding utf8 $ImportLog
if ($LASTEXITCODE -ne 0) { Write-Error "Godot asset import failed. See $ImportLog"; exit $LASTEXITCODE }
& $GodotExe --headless --path $Root --script 'res://validate_import.gd' *>&1 | Out-File -Encoding utf8 $AuditLog
if ($LASTEXITCODE -ne 0) { Write-Error "Godot model audit failed. See $AuditLog"; exit $LASTEXITCODE }
if (-not (Select-String -Path $AuditLog -SimpleMatch 'GODOT ENGINE IMPORT CHECK PASS' -Quiet)) {
    Write-Error "Audit did not print success marker; inspect $AuditLog"; exit 2
}
Write-Output 'Godot import and structural audit passed. This does not imply visual QC.'
Write-Output "Engine logs: $LogDir"
