# PowerShell script to push code to GitHub repository
# Run this script after Git is installed

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub Push Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
Write-Host "Checking for Git installation..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Git not found"
    }
    Write-Host "✓ Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Git first:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://git-scm.com/download/win" -ForegroundColor White
    Write-Host "2. Or run: winget install --id Git.Git -e --source winget" -ForegroundColor White
    Write-Host "3. Restart your terminal after installation" -ForegroundColor White
    exit 1
}

Write-Host ""

# Initialize git repository if not already initialized
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Green
    git init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to initialize Git repository" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ Git repository already initialized" -ForegroundColor Green
}

# Add remote repository
Write-Host "Configuring remote repository..." -ForegroundColor Green
git remote remove origin 2>$null
git remote add origin https://github.com/mmammadali/personal-ai-assistant-.git
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to add remote repository" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Remote repository configured" -ForegroundColor Green

# Add all files
Write-Host "Adding files to staging area..." -ForegroundColor Green
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to add files" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Files added" -ForegroundColor Green

# Check if there are changes to commit
$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "⚠ No changes to commit" -ForegroundColor Yellow
} else {
    # Commit changes
    Write-Host "Committing changes..." -ForegroundColor Green
    git commit -m "Initial commit: Personal AI Assistant project"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to commit changes" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Changes committed" -ForegroundColor Green
}

# Set branch to main
Write-Host "Setting branch to 'main'..." -ForegroundColor Green
git branch -M main 2>$null
Write-Host "✓ Branch set to 'main'" -ForegroundColor Green

# Push to GitHub
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Green
Write-Host "Note: You may be prompted for GitHub credentials" -ForegroundColor Yellow
Write-Host "If asked for password, use a Personal Access Token (not your GitHub password)" -ForegroundColor Yellow
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✓ Success! Code pushed to GitHub" -ForegroundColor Green
    Write-Host "Repository: https://github.com/mmammadali/personal-ai-assistant-" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "✗ Push failed. Common issues:" -ForegroundColor Red
    Write-Host "1. Authentication required - use Personal Access Token" -ForegroundColor Yellow
    Write-Host "2. Repository doesn't exist or you don't have access" -ForegroundColor Yellow
    Write-Host "3. Network connectivity issues" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "See GITHUB_SETUP.md for troubleshooting help" -ForegroundColor Cyan
    exit 1
}

