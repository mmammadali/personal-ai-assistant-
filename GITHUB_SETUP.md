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

**Step-by-Step Guide to Create a Personal Access Token:**

1. **Go to GitHub Token Settings**
   - Direct link: https://github.com/settings/tokens
   - Or navigate: GitHub → Your Profile Picture (top right) → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**

2. **Generate New Token**
   - Click the **"Generate new token"** button
   - Select **"Generate new token (classic)"**

3. **Configure Your Token**
   - **Note**: Give it a descriptive name (e.g., "Push to personal-ai-assistant repo")
   - **Expiration**: Choose how long the token should be valid:
     - 30 days, 60 days, 90 days
     - Or "No expiration" (less secure but convenient)
   - **Select scopes**: Check the **`repo`** checkbox
     - This gives full control of private repositories
     - Includes: repo:status, repo_deployment, public_repo, repo:invite, security_events

4. **Generate and Copy Token**
   - Scroll down and click **"Generate token"** (green button at the bottom)
   - **IMPORTANT**: Copy the token immediately! It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - You won't be able to see it again after you leave the page
   - Save it somewhere safe (password manager, secure note, etc.)

5. **Use the Token**
   - When Git prompts you for credentials during `git push`:
     - **Username**: Your GitHub username (`mmammadali`)
     - **Password**: Paste your Personal Access Token (NOT your GitHub password)

**Security Note**: Treat your Personal Access Token like a password. Never share it or commit it to your repository.

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

