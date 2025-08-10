param(
  [switch]$Clean
)

$ErrorActionPreference = 'Stop'

$androidDir = Join-Path $PSScriptRoot 'android'
if (-not (Test-Path $androidDir)) {
  Write-Error "Android folder not found: $androidDir"
}

if ($Clean) {
  Write-Host "Cleaning build outputs..." -ForegroundColor Cyan
  Push-Location $androidDir
  try {
    & .\gradlew.bat clean
  } finally {
    Pop-Location
  }
}

Write-Host "Building release APK for DigitalSignageTV..." -ForegroundColor Cyan
Push-Location $androidDir
try {
  & .\gradlew.bat assembleRelease
} finally {
  Pop-Location
}

Write-Host "Done. If successful, APK is under android\\app\\build\\outputs\\apk\\release" -ForegroundColor Green
