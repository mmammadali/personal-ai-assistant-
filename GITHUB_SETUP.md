# GitHub Repository Setup Guide

## Quick Setup (After Git Installation)

Once Git is installed, run one of these commands:

### Option 1: Use the PowerShell Script
```powershell
.\push_to_github.ps1
```

### Option 2: Use the Batch File
Double-click `push_to_github.bat`

### Option 3: Manual Commands
```bash
git init
git remote add origin https://github.com/mmammadali/personal-ai-assistant-.git
git add .
git commit -m "Initial commit: Personal AI Assistant project"
git branch -M main
git push -u origin main
```

## Installing Git

### Method 1: Using winget (Windows Package Manager)
```powershell
winget install --id Git.Git -e --source winget
```
**Note:** This may require administrator privileges. Right-click PowerShell and select "Run as Administrator".

### Method 2: Download from Official Website
1. Visit: https://git-scm.com/download/win
2. Download and run the installer
3. During installation, select "Git from the command line and also from 3rd-party software"
4. Restart your terminal/IDE after installation

### Method 3: Using Chocolatey (if installed)
```powershell
choco install git
```

## Authentication

When pushing for the first time, GitHub will require authentication:

### Option 1: Personal Access Token (Recommended)
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate a new token with `repo` scope
3. Use the token as your password when prompted

### Option 2: GitHub Desktop
Install GitHub Desktop for a GUI-based approach:
https://desktop.github.com/

## Troubleshooting

### Git not found after installation
- Restart your terminal/IDE
- Check if Git is in PATH: `$env:PATH -split ';' | Select-String -Pattern 'git'`
- Manually add Git to PATH if needed: `C:\Program Files\Git\bin`

### Authentication failed
- Use Personal Access Token instead of password
- Check if 2FA is enabled on your GitHub account
- Verify repository URL is correct

### Push rejected
- Make sure the repository exists and is empty (or you have write access)
- Check if you're pushing to the correct branch (`main`)

