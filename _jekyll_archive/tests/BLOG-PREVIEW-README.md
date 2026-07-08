# Blog Preview Scripts

Quick Docker-based blog preview scripts for local development.

## Quick Start

### Option 1: Simple Commands (Recommended)
```powershell
# Start blog preview
.\blog-dev.ps1 start

# View your blog at: http://localhost:4000

# Stop when done
.\blog-dev.ps1 stop
```

### Option 2: Full Control
```powershell
# Interactive mode (shows logs, Ctrl+C to stop)
.\start-blog-preview.ps1

# Background mode (continues running)
.\start-blog-preview.ps1 -Detached

# Stop services
.\start-blog-preview.ps1 -Stop
```

## Available Scripts

### `blog-dev.ps1` - Simple Commands
Quick wrapper for common tasks:

```powershell
.\blog-dev.ps1 start     # Start blog in background
.\blog-dev.ps1 stop      # Stop all services
.\blog-dev.ps1 build     # Rebuild containers
.\blog-dev.ps1 restart   # Restart Jekyll only
.\blog-dev.ps1 logs      # Show live logs
.\blog-dev.ps1 status    # Check current status
.\blog-dev.ps1 help      # Show help
```

### `start-blog-preview.ps1` - Full Featured
Complete blog preview launcher with all options:

```powershell
# Basic usage
.\start-blog-preview.ps1                 # Interactive mode
.\start-blog-preview.ps1 -Detached       # Background mode
.\start-blog-preview.ps1 -Build          # Rebuild first
.\start-blog-preview.ps1 -Stop           # Stop services
.\start-blog-preview.ps1 -Remove         # Remove containers
.\start-blog-preview.ps1 -Help           # Show help
```

## What These Scripts Do

### Services Started
1. **Jekyll Server** - Serves your blog at http://localhost:4000
2. **File Watcher** - Automatically converts:
   - Jupyter notebooks (`.ipynb`) from `_notebooks/`
   - Word documents (`.docx`, `.doc`) from `_word/`
3. **Live Preview** - See changes by refreshing your browser

### First Time Setup
The scripts will automatically:
- Check Docker availability
- Set proper file permissions
- Build required containers (may take 2-3 minutes first time)
- Start all services

### Troubleshooting

#### Containers Won't Start
```powershell
# Rebuild everything from scratch
.\blog-dev.ps1 build
```

#### Check What's Running
```powershell
# View status and logs
.\blog-dev.ps1 status
.\blog-dev.ps1 logs
```

#### Clean Restart
```powershell
# Stop everything and start fresh
.\blog-dev.ps1 stop
.\start-blog-preview.ps1 -Remove
.\blog-dev.ps1 build
```

## Requirements

- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop)
- **PowerShell** - Available on Windows, macOS, and Linux
- **Blog repository** - Run scripts from your blog root directory

## Development Workflow

### Typical Session
```powershell
# 1. Start blog preview
.\blog-dev.ps1 start

# 2. Open browser to http://localhost:4000

# 3. Edit your posts, notebooks, or Word docs

# 4. Refresh browser to see changes

# 5. When done
.\blog-dev.ps1 stop
```

### Working with Notebooks
1. Add `.ipynb` files to `_notebooks/` folder
2. The watcher service automatically converts them to blog posts
3. Refresh browser to see new posts

### Working with Word Documents
1. Add `.docx` or `.doc` files to `_word/` folder
2. The watcher service automatically converts them to blog posts
3. Refresh browser to see new posts

## Advanced Usage

### Background Development
```powershell
# Start in background and continue working
.\blog-dev.ps1 start

# Check status anytime
.\blog-dev.ps1 status

# View logs when needed
.\blog-dev.ps1 logs

# Stop when done
.\blog-dev.ps1 stop
```

### Container Management
```powershell
# Restart just Jekyll (faster than full restart)
.\blog-dev.ps1 restart

# Full rebuild (if you changed Docker configs)
.\blog-dev.ps1 build

# Remove everything and start over
.\start-blog-preview.ps1 -Remove
.\blog-dev.ps1 build
```

### Direct Docker Commands
If you prefer using Docker directly:

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose stop

# View logs
docker-compose logs -f

# Restart Jekyll only
docker-compose restart jekyll
```

## File Structure

Your blog should have this structure:
```
your-blog/
├── _notebooks/          # Jupyter notebooks
├── _word/              # Word documents
├── _posts/             # Generated markdown posts
├── docker-compose.yml  # Docker configuration
├── Makefile           # Make commands
├── blog-dev.ps1       # Simple commands (this script)
├── start-blog-preview.ps1  # Full featured script
└── ...
```

## Tips

- **First run takes longer** - Docker needs to download and build images
- **No auto-reload** - Manually refresh browser to see changes
- **File permissions** - Scripts automatically handle Windows/Docker permission issues
- **Multiple projects** - Each blog needs its own terminal/container instance
- **Port conflicts** - Only one blog can run on port 4000 at a time

## Troubleshooting Common Issues

### "Docker not found"
Install Docker Desktop from https://www.docker.com/products/docker-desktop

### "Permission denied" errors
The scripts handle this automatically, but you can also run:
```powershell
.\start-blog-preview.ps1 -Build
```

### "Port 4000 already in use"
Stop other blog instances:
```powershell
.\blog-dev.ps1 stop
```

### Containers keep failing
Clean rebuild:
```powershell
.\start-blog-preview.ps1 -Remove
.\blog-dev.ps1 build
```

### Changes not showing
1. Check if file watcher is running: `.\blog-dev.ps1 status`
2. Manually refresh browser
3. Check logs: `.\blog-dev.ps1 logs`

---

**Happy blogging! 🚀**