@echo off
echo Initializing Git repository...

REM Initialize git repository if not already initialized
if not exist ".git" (
    git init
)

REM Add remote repository
echo Adding remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/mmammadali/personal-ai-assistant-.git

REM Add all files
echo Adding all files...
git add .

REM Commit changes
echo Committing changes...
git commit -m "Initial commit: Personal AI Assistant project"

REM Push to GitHub
echo Pushing to GitHub...
git branch -M main
git push -u origin main

echo Done! Your code has been pushed to GitHub.
pause

