$ErrorActionPreference = "Stop"

$rootDir = Split-Path -Parent $PSScriptRoot
Set-Location $rootDir

if (-not (Test-Path ".env")) {
    Copy-Item ".env.development" ".env"
    Write-Host "Created .env from .env.development"
}

Write-Host "Installing frontend workspace dependencies..."
pnpm install

Write-Host "Building and starting containers..."
docker compose up --build -d

Write-Host "PassHub is starting:"
Write-Host "  Web      -> http://localhost:5173"
Write-Host "  API      -> http://localhost:8000/api/v1/docs"
Write-Host "  MinIO    -> http://localhost:9001"
Write-Host "  PgAdmin  -> http://localhost:5050"
