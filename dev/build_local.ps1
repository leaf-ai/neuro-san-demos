# PowerShell script to check/create Docker volume, build the image, and run the container on Windows
param(
    [string]$VolumeName = "neuro-san-studio-history",
    [string]$ImageName = "neuro-san-dev",
    [string]$ContainerName = "neuro-san-container",
    [string]$DockerfilePath = "dev/Dockerfile"
)

$ErrorActionPreference = 'Stop'

Write-Host "Checking Docker volume $VolumeName..."
try {
    docker volume inspect $VolumeName | Out-Null
    Write-Host "Volume $VolumeName exists."
} catch {
    Write-Host "Volume $VolumeName does not exist. Creating..."
    docker volume create $VolumeName
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create volume $VolumeName."
        exit 1
    }
    Write-Host "Volume $VolumeName created successfully."
}

Write-Host "Building Docker image $ImageName..."
docker build -t $ImageName -f $DockerfilePath .
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to build Docker image $ImageName."
    exit 1
}
Write-Host "Docker image $ImageName built successfully."

# Prepare host path for volume mount
$hostPath = (Get-Location).Path.Replace('\\','/')

# Convert entrypoint.sh to Unix (LF) line endings before running Docker
$entrypointPath = "$PSScriptRoot\entrypoint.sh"
(Get-Content $entrypointPath -Raw) -replace "`r`n", "`n" | Set-Content -NoNewline -Encoding utf8 $entrypointPath

Write-Host "Running Docker container $ContainerName..."
# Always expose port 8005 for consistency across all platforms
# The entrypoint script will determine if it needs to start the proxy server
# Pass WINDOWS_ENV=true to indicate we're on Windows or WSL
docker run -it --env-file .env --rm --name $ContainerName `
    -p 4173:4173 `
    -p 30013:30013 `
    -p 8005:8005 `
    -v "${VolumeName}:/home/user/" `
    -v "${hostPath}:/home/user/app/" `
    --entrypoint bash `
    $ImageName -c "bash /home/user/app/dev/entrypoint.sh"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to run Docker container $ContainerName."
    exit 1
}
Write-Host "Docker container $ContainerName ran successfully."