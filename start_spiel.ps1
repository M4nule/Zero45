# Zero45 – start the game (Windows)
#   .\start_spiel.ps1            network mode (teams in the Wi-Fi)
#   .\start_spiel.ps1 -Local     local mode with single-player game   (-Solo: opens the single-player game directly)
#   -Password secret  changes the game master password
#   -HostRemote       game master page from other devices too (default: this computer only)
#   -Workers 3        number of simultaneous simulation processes (default: automatic, by free memory)
param([int]$Port = 8000, [switch]$Local, [switch]$Solo, [string]$Password = "", [switch]$HostRemote, [int]$Workers = 0)
Set-Location $PSScriptRoot
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
if (-not $Local -and -not $Solo) {
    # in "public" networks Windows blocks access from other devices
    try {
        foreach ($np in @(Get-NetConnectionProfile -ErrorAction Stop | Where-Object { $_.NetworkCategory -eq "Public" })) {
            Write-Host "Warning: network '$($np.Name)' is classified as 'Public' - other devices cannot connect." -ForegroundColor Yellow
            Write-Host "         Fix (own Wi-Fi/hotspot only): Settings > Network & Internet > network properties > 'Private network'" -ForegroundColor Yellow
        }
    } catch { }
}
$args_ = @("run", "--frozen", "python", "-m", "ptz.server.app", "--port", "$Port")
if ($Local) { $args_ += "--local" }
if ($Solo) { $args_ += "--solo" }
if ($Password) { $args_ += @("--password", $Password) }
if ($HostRemote) { $args_ += "--host-remote" }
if ($Workers -gt 0) { $args_ += @("--workers", "$Workers") }
& uv @args_
