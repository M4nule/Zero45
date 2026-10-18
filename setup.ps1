# Zero45 – setup on Windows (once)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv ..." -ForegroundColor Cyan
    # official install script from Astral, fixed version (ExecutionPolicy Bypass only for this call)
    powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/0.11.32/install.ps1 | iex"
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}
Write-Host "Installing Python and packages (1-3 minutes) ..." -ForegroundColor Cyan
# --frozen: installs exactly the versions from uv.lock (with checksums), nothing newer
uv sync --frozen
Write-Host "Test: the model calculates one year ..." -ForegroundColor Cyan
uv run --frozen python -c "from ptz.game.runner import warmup; warmup(); print('OK')"
Write-Host "`nDone. Start with:  .\start_spiel.ps1   (single-player game: .\start_spiel.ps1 -Solo)" -ForegroundColor Green
