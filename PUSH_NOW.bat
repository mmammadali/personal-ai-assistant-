@echo off
echo ========================================
echo Pushing to GitHub
echo ========================================
echo.
echo When prompted for credentials:
echo   Username: mmammadali
echo   Password: Paste your Personal Access Token (NOT your GitHub password)
echo.
echo Press any key to continue...
pause >nul
echo.

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Code pushed to GitHub!
    echo Repository: https://github.com/mmammadali/personal-ai-assistant-
    echo ========================================
) else (
    echo.
    echo Push failed. Make sure you:
    echo 1. Have a Personal Access Token ready
    echo 2. Use the token as your password (not your GitHub password)
    echo 3. Have internet connectivity
)

echo.
pause













