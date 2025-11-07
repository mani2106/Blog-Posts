# Quick Blog Development Commands
# Simplified wrapper for common blog development tasks

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "build", "restart", "logs", "status", "help")]
    [string]$Command = "help"
)

function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host $msg -ForegroundColor Yellow }

switch ($Command.ToLower()) {
    "start" {
        Write-Info "Starting blog preview..."
        .\tests\start-blog-preview.ps1 -Detached
    }

    "stop" {
        Write-Info "Stopping blog services..."
        .\tests\start-blog-preview.ps1 -Stop
    }

    "build" {
        Write-Info "Rebuilding containers..."
        .\tests\start-blog-preview.ps1 -Build -Detached
    }

    "restart" {
        Write-Info "Restarting Jekyll server..."
        docker-compose restart jekyll
        Write-Success "Jekyll restarted"
        Write-Info "Blog: http://localhost:4000"
    }

    "logs" {
        Write-Info "Showing recent logs..."
        docker-compose logs --tail=50 -f
    }

    "status" {
        Write-Info "Current status:"
        docker-compose ps

        try {
            $response = Invoke-WebRequest -Uri "http://localhost:4000" -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "Blog accessible at http://localhost:4000"
            }
        } catch {
            Write-Warning "Blog not accessible at http://localhost:4000"
        }
    }

    "help" {
        Write-Host "Blog Development Helper" -ForegroundColor Green
        Write-Host "======================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Usage: .\blog-dev.ps1 [command]" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Commands:" -ForegroundColor Yellow
        Write-Host "  start    - Start blog preview in background"
        Write-Host "  stop     - Stop all blog services"
        Write-Host "  build    - Rebuild containers and start"
        Write-Host "  restart  - Restart Jekyll server only"
        Write-Host "  logs     - Show live logs"
        Write-Host "  status   - Show current status"
        Write-Host "  help     - Show this help"
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Cyan
        Write-Host "  .\blog-dev.ps1 start"
        Write-Host "  .\blog-dev.ps1 logs"
        Write-Host "  .\blog-dev.ps1 stop"
        Write-Host ""
        Write-Host "Blog URL: http://localhost:4000" -ForegroundColor Green
    }

    default {
        Write-Warning "Unknown command: $Command"
        Write-Info "Use .\blog-dev.ps1 help for available commands"
    }
}