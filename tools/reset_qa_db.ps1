$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot

Push-Location $repoRoot
try {
    Write-Host 'Starting the isolated pashusetu_qa database...'
    docker compose up -d db_qa

    Write-Host 'Applying migrations to pashusetu_qa...'
    docker compose run --rm qa_seed alembic upgrade head

    Write-Host 'Resetting and seeding canonical synthetic QA fixtures...'
    docker compose run --rm qa_seed python -m app.db.qa_seed reset-seed

    Write-Host 'Isolated QA database is ready.'
}
finally {
    Pop-Location
}
