# Auto-detect Git and push to GitHub
$gitPaths = @(
    "git",
    "C:\Program Files\Git\bin\git.exe",
    "C:\Program Files\Git\cmd\git.exe",
    "C:\Program Files (x86)\Git\bin\git.exe",
    "C:\Program Files (x86)\Git\cmd\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\bin\git.exe",
    "$env:ProgramFiles\Git\bin\git.exe"
)

$gitCmd = $null
foreach ($path in $gitPaths) {
    try {
        if ($path -eq "git") {
            $result = & git --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $gitCmd = "git"
                break
            }
        } else {
            if (Test-Path $path) {
                $result = & $path --version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $gitCmd = $path
                    break
                }
            }
        }
    } catch {
        continue
    }
}

if (-not $gitCmd) {
    Write-Host "Git not found. Please restart your terminal/IDE after installing Git." -ForegroundColor Red
    Write-Host "Or provide the Git installation path." -ForegroundColor Yellow
    exit 1
}

Write-Host "Found Git: $gitCmd" -ForegroundColor Green
Write-Host ""

# Function to run git commands
function Run-Git {
    param([string]$command)
    $args = $command -split '\s+', 2
    if ($gitCmd -eq "git") {
        & git $args[0] $args[1]
    } else {
        & $gitCmd $args[0] $args[1]
    }
}

# Initialize repository
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Green
    Run-Git "init"
}

# Configure remote
Write-Host "Configuring remote..." -ForegroundColor Green
Run-Git "remote remove origin" 2>$null
Run-Git "remote add origin https://github.com/mmammadali/personal-ai-assistant-.git"

# Add files
Write-Host "Adding files..." -ForegroundColor Green
Run-Git "add ."

# Commit
Write-Host "Committing..." -ForegroundColor Green
Run-Git "commit -m `"Initial commit: Personal AI Assistant project`""

# Set branch
Write-Host "Setting branch to main..." -ForegroundColor Green
Run-Git "branch -M main" 2>$null

# Push
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Green
Write-Host "Note: You may be prompted for credentials. Use a Personal Access Token if asked for password." -ForegroundColor Yellow
Write-Host ""
Run-Git "push -u origin main"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Success! Code pushed to GitHub!" -ForegroundColor Green
    Write-Host "Repository: https://github.com/mmammadali/personal-ai-assistant-" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Push may have failed. Check the output above." -ForegroundColor Yellow
}

