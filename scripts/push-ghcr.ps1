<#
PowerShell helper to build and push displayads images to GHCR (ghcr.io/japsterr)
Usage: Open PowerShell, run: .\scripts\push-ghcr.ps1
You will be prompted for your GHCR username (defaults to current user) and PAT (read-only input).
#>

param(
    # Default to the repository owner namespace to avoid using the local Windows username by mistake
    [string]$GHCRUser = 'japsterr'
)

Write-Host "Building and pushing images to ghcr.io/japsterr..."

# Simple Docker availability check
try {
    docker --version | Out-Null
} catch {
    Write-Error "Docker CLI not found or not in PATH. Install Docker Desktop and try again."
    exit 1
}

# Allow non-interactive usage via GHCR_TOKEN env var (useful for CI or if you don't want prompts)
if ($env:GHCR_TOKEN) {
    $plainToken = $env:GHCR_TOKEN
} else {
    Write-Host "Enter GHCR Personal Access Token (scope: write:packages). It will not be echoed."
    $secureToken = Read-Host -AsSecureString -Prompt "GHCR Personal Access Token"
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
    $plainToken = [Runtime.InteropServices.Marshal]::PtrToStringAuto($ptr)
}

Write-Host "Logging in to ghcr.io as $GHCRUser using password-stdin..."
try {
    # Use password-stdin to avoid exposing token in process arguments
    $plainToken | docker login ghcr.io -u $GHCRUser --password-stdin | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "docker login returned exit code $LASTEXITCODE"
    }
} catch {
    Write-Error "Docker login failed: $($_.Exception.Message)"
    Write-Host "Common causes and fixes:" -ForegroundColor Yellow
    Write-Host " - Wrong username: set -GHCRUser to the GitHub account that owns the target GHCR namespace (example: -GHCRUser japsterr)"
    Write-Host " - Wrong/insufficient PAT scopes: recreate a PAT with 'write:packages' (and optionally 'read:packages' and 'repo' if pushing from a private repo)."
    Write-Host " - Token belongs to a different GitHub account than the target namespace (you must authenticate as the owner or a collaborator with package write access)."
    Write-Host " - To push from CI, set the repository secret GHCR_TOKEN to a PAT belonging to the repository owner or use the Actions workflow which logs in as \\$GITHUB_ACTOR."
    if (-not $env:GHCR_TOKEN) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) | Out-Null }
    exit 1
}
if (-not $env:GHCR_TOKEN) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) | Out-Null }

# Build API image
Write-Host "Building API image..."
docker build -t ghcr.io/japsterr/displayads-api:latest -f Dockerfile .
if ($LASTEXITCODE -ne 0) { Write-Error "API build failed"; exit 1 }

Write-Host "Pushing API image..."
docker push ghcr.io/japsterr/displayads-api:latest
if ($LASTEXITCODE -ne 0) { Write-Error "API push failed"; exit 1 }

# Build frontend
Write-Host "Building frontend image..."
docker build -t ghcr.io/japsterr/displayads-frontend:latest -f Workspace/Dockerfile Workspace
if ($LASTEXITCODE -ne 0) { Write-Error "Frontend build failed"; exit 1 }

Write-Host "Pushing frontend image..."
docker push ghcr.io/japsterr/displayads-frontend:latest
if ($LASTEXITCODE -ne 0) { Write-Error "Frontend push failed"; exit 1 }

Write-Host "Done. Images pushed to ghcr.io/japsterr/."

# Clear sensitive variable
$plainToken = $null
Remove-Variable plainToken -ErrorAction SilentlyContinue
