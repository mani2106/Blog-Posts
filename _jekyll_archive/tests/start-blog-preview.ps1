# Blog Preview Launcher
# Quick Docker-based blog preview script based on fastpages development guide

param(
    [switch]$Detached,
    [switch]$Build,
    [switch]$Stop,
    [switch]$Remove,
    [switch]$Help
)

# Color functions for better output
function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host $msg -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host $msg -ForegroundColor Red }

function Show-Help {
    Write-Host "Blog Preview Launcher" -ForegroundColor Green
    Write-Host "=====================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "  .\start-blog-preview.ps1                 # Start blog preview (interactive)"
    Write-Host "  .\start-blog-preview.ps1 -Detached       # Start in background"
    Write-Host "  .\start-blog-preview.ps1 -Build          # Rebuild containers first"
    Write-Host "  .\start-blog-preview.ps1 -Stop           # Stop all services"
    Write-Host "  .\start-blog-preview.ps1 -Remove         # Remove all containers"
    Write-Host "  .\start-blog-preview.ps1 -Help           # Show this help"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  # Quick start (most common)"
    Write-Host "  .\start-blog-preview.ps1"
    Write-Host ""
    Write-Host "  # Start in background and continue working"
    Write-Host "  .\start-blog-preview.ps1 -Detached"
    Write-Host ""
    Write-Host "  # Rebuild everything from scratch"
    Write-Host "  .\start-blog-preview.ps1 -Build"
    Write-Host ""
    Write-Host "Services:" -ForegroundColor Cyan
    Write-Host "  - Jekyll Server: http://localhost:4000"
    Write-Host "  - Auto-conversion: Monitors .ipynb and .docx files"
    Write-Host "  - Live reload: Manual browser refresh required"
}

function Test-Docker {
    Write-Info "Checking Docker availability..."

    try {
        $dockerVersion = docker --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker found: $dockerVersion"
        } else {
            Write-Error "Docker not found. Please install Docker Desktop first."
            Write-Info "Download from: https://www.docker.com/products/docker-desktop"
            exit 1
        }
    } catch {
        Write-Error "Docker not available: $($_.Exception.Message)"
        exit 1
    }

    try {
        $composeVersion = docker-compose --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker Compose found: $composeVersion"
        } else {
            Write-Error "Docker Compose not found."
            exit 1
        }
    } catch {
        Write-Error "Docker Compose not available: $($_.Exception.Message)"
        exit 1
    }
}

function Set-Permissions {
    Write-Info "Setting file permissions..."
    try {
        # Equivalent of chmod -R u+rw .
        Get-ChildItem -Recurse | ForEach-Object {
            if (-not $_.PSIsContainer) {
                $_.IsReadOnly = $false
            }
        }

        # Specific permission for Gemfile.lock (equivalent of chmod 777)
        if (Test-Path "Gemfile.lock") {
            $gemfileLock = Get-Item "Gemfile.lock"
            $gemfileLock.IsReadOnly = $false
        }

        Write-Success "Permissions updated"
    } catch {
        Write-Warning "Could not update all permissions: $($_.Exception.Message)"
    }
}

function Stop-Services {
    Write-Info "Stopping blog services..."

    try {
        # Stop docker-compose services
        docker-compose stop 2>$null | Out-Null

        # Stop any remaining fastpages containers
        $fastpagesContainers = docker ps --format "table {{.Names}}" | Where-Object { $_ -match "fastpages" }
        if ($fastpagesContainers) {
            Write-Info "Found running fastpages containers, stopping them..."
            docker ps | Select-String "fastpages" | ForEach-Object {
                $containerId = ($_ -split '\s+')[0]
                docker stop $containerId 2>$null | Out-Null
            }
        }

        Write-Success "Services stopped"
    } catch {
        Write-Warning "Error stopping services: $($_.Exception.Message)"
    }
}

function Remove-Containers {
    Write-Info "Removing blog containers..."

    try {
        Stop-Services
        docker-compose rm -f 2>$null | Out-Null
        Write-Success "Containers removed"
    } catch {
        Write-Warning "Error removing containers: $($_.Exception.Message)"
    }
}

function Build-Containers {
    Write-Info "Building blog containers (this may take a few minutes)..."

    try {
        Set-Permissions

        # Stop and remove existing containers
        docker-compose stop 2>$null | Out-Null
        docker-compose rm -f 2>$null | Out-Null

        # Build fastpages Jekyll image
        Write-Info "Building fastpages Jekyll image..."
        docker build --no-cache -t fastai/fastpages-jekyll -f _action_files/fastpages-jekyll.Dockerfile .

        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to build Jekyll image"
            exit 1
        }

        # Build docker-compose services
        Write-Info "Building docker-compose services..."
        docker-compose build --force-rm --no-cache

        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to build services"
            exit 1
        }

        Write-Success "Containers built successfully"
    } catch {
        Write-Error "Build failed: $($_.Exception.Message)"
        exit 1
    }
}

function Start-BlogPreview {
    param([bool]$RunDetached = $false)

    Write-Info "Starting blog preview..."

    try {
        Set-Permissions

        # Clean up any existing containers
        docker-compose down --remove-orphans 2>$null | Out-Null

        if ($RunDetached) {
            Write-Info "Starting services in background..."
            docker-compose up -d

            if ($LASTEXITCODE -eq 0) {
                Write-Success "Blog services started in background"
                Write-Info "Blog preview: http://localhost:4000"
                Write-Info "Services running in background. Use -Stop to stop them."

                # Wait a moment and check if services are running
                Start-Sleep -Seconds 3
                $runningServices = docker-compose ps --services --filter "status=running"
                if ($runningServices) {
                    Write-Success "Running services: $($runningServices -join ', ')"
                } else {
                    Write-Warning "No services appear to be running. Check logs with: docker-compose logs"
                }
            } else {
                Write-Error "Failed to start services"
                exit 1
            }
        } else {
            Write-Info "Starting services (interactive mode)..."
            Write-Info "Blog will be available at: http://localhost:4000"
            Write-Info "Press Ctrl+C to stop services"
            Write-Info ""

            # Start in interactive mode
            docker-compose up
        }

    } catch {
        Write-Error "Failed to start blog preview: $($_.Exception.Message)"
        exit 1
    }
}

function Show-Status {
    Write-Info "Blog Preview Status"
    Write-Info "====================="

    try {
        $runningContainers = docker-compose ps
        if ($runningContainers) {
            Write-Host $runningContainers
        } else {
            Write-Info "No containers currently running"
        }

        # Test if blog is accessible
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:4000" -TimeoutSec 3 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "Blog is accessible at http://localhost:4000"
            }
        } catch {
            Write-Info "Blog not currently accessible at http://localhost:4000"
        }

    } catch {
        Write-Warning "Could not get status: $($_.Exception.Message)"
    }
}

# Main script logic
if ($Help) {
    Show-Help
    exit 0
}

# Get the script directory and navigate to parent (blog root)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BlogRoot = Split-Path -Parent $ScriptDir

# Change to blog root directory
Push-Location $BlogRoot

# Check if we're in the right directory
if (-not (Test-Path "docker-compose.yml")) {
    Write-Error "docker-compose.yml not found in $BlogRoot"
    Pop-Location
    exit 1
}

# Test Docker availability
Test-Docker

# Handle different operations
if ($Remove) {
    Remove-Containers
} elseif ($Stop) {
    Stop-Services
    Show-Status
} elseif ($Build) {
    Build-Containers
    Write-Info "Build complete. Starting blog preview..."
    Start-BlogPreview -RunDetached:$Detached
} else {
    # Default: start blog preview
    Write-Info "Starting blog preview..."
    Write-Info "Tip: Use -Build if containers won't start properly"
    Write-Info ""

    Start-BlogPreview -RunDetached:$Detached
}

Write-Info ""
Write-Info "Useful commands:"
Write-Info "  .\start-blog-preview.ps1 -Stop     # Stop services"
Write-Info "  .\start-blog-preview.ps1 -Build    # Rebuild containers"
Write-Info "  docker-compose logs                 # View logs"
Write-Info "  docker-compose restart jekyll      # Restart Jekyll only"

# Return to original directory
Pop-Location
