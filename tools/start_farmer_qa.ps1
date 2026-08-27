param(
    [switch]$SkipPubGet
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "PashuSetu Farmer QA launcher"
Write-Host "Repository: $repoRoot"

Push-Location $repoRoot
try {
    Write-Host "Checking Docker engine..."
    docker info *> $null

    Write-Host "Starting local PostgreSQL and API services..."
    docker compose up -d db api

    Write-Host "Waiting for API health..."
    $healthy = $false
    for ($i = 0; $i -lt 30; $i++) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:8000/health' -TimeoutSec 2
            if ($response.StatusCode -eq 200) {
                $healthy = $true
                break
            }
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }

    if (-not $healthy) {
        throw 'Local API did not become healthy at http://localhost:8000/health. Check Docker/API logs.'
    }

    Write-Host "Applying non-destructive local migrations..."
    docker compose exec -T api alembic upgrade head

    $farmerApp = Join-Path $repoRoot 'apps\farmer_mobile'
    Push-Location $farmerApp
    try {
        if (-not $SkipPubGet) {
            Write-Host "Resolving Farmer Flutter dependencies..."
            flutter pub get
        }

        Write-Host "Checking Chrome device..."
        $devices = flutter devices
        if (($devices | Out-String) -notmatch 'Chrome') {
            throw 'Flutter does not currently detect Chrome. Install/enable Chrome and rerun.'
        }

        Write-Host "Launching Farmer app in Chrome..."
        Write-Host "Keep this terminal open while testing. Press q in the Flutter terminal to stop the app."
        flutter run -d chrome
    }
    finally {
        Pop-Location
    }
}
finally {
    Pop-Location
}
