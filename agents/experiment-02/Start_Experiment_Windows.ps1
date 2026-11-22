param(
  [switch]$TestOnly,
  [string]$ProducerModel='qwen3.5:4b',
  [string]$AuditorModel='qwen3-vl:4b'
)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = 'py'
try { & $python -3 --version | Out-Null } catch { $python = 'python' }
Write-Host 'Villa Verse Exp02 — separate-context Producer / Auditor'
Write-Host 'This experiment runs only while this command is active.'
& $python -m pip show cryptography *> $null
if ($LASTEXITCODE -ne 0) {
  Write-Host 'Installing free Python cryptography package...'
  & $python -m pip install --user cryptography
  if ($LASTEXITCODE -ne 0) { throw 'Could not install cryptography' }
}
if ($TestOnly) {
  & $python -m unittest discover -s tests -p 'test_local_integration.py' -v
  if ($LASTEXITCODE -ne 0) { throw 'Infrastructure tests failed' }
  exit 0
}
& $python src/setup_owner_keys.py
if ($LASTEXITCODE -ne 0) { throw 'Local owner key initialization failed' }
try { $version = & ollama --version } catch { throw 'Ollama executable not found. Install and start Ollama first.' }
Write-Host $version
try { $models = & ollama list } catch { throw 'Ollama is not reachable; start Ollama locally first.' }
Write-Host $models
& $python src/orchestrator.py --backend ollama --model-producer $ProducerModel --model-auditor $AuditorModel
if ($LASTEXITCODE -ne 0) {
  Write-Host 'Run failed. If a required model is missing, run: ollama pull qwen3.5:4b and ollama pull qwen3-vl:4b.'
  exit $LASTEXITCODE
}
Write-Host 'Results: run/<run-id>/public_result.json. Private reports are encrypted.'
