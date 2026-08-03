@echo off
REM ============================================================
REM push_to_github.bat
REM Push toan bo file trong folder hien tai len GitHub repo
REM Repo: https://github.com/HONGPHUC1210/Project_Actuaire.git
REM ============================================================

REM Di chuyen vao dung folder chua file .bat nay (bat ke chay tu dau)
cd /d "%~dp0"

echo.
echo === Thu muc lam viec: %cd% ===
echo.

REM --- Kiem tra git da cai chua ---
where git >nul 2>nul
if errorlevel 1 (
    echo [LOI] Khong tim thay git. Hay cai Git for Windows truoc: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM --- Neu chua co .git thi khoi tao ---
if not exist ".git" (
    echo Chua co repo git, dang khoi tao...
    git init
    git branch -M main
)

REM --- Gan remote "origin", neu da ton tai thi cap nhat lai URL ---
git remote get-url origin >nul 2>nul
if errorlevel 1 (
    git remote add origin https://github.com/HONGPHUC1210/Project_Actuaire.git
) else (
    git remote set-url origin https://github.com/HONGPHUC1210/Project_Actuaire.git
)

REM --- Add toan bo file ---
echo.
echo === Dang add toan bo file... ===
git add -A

REM --- Commit (co the sua message trong bien COMMIT_MSG ben duoi) ---
set COMMIT_MSG=Update project files

git diff --cached --quiet
if errorlevel 1 (
    echo === Dang commit voi message: "%COMMIT_MSG%" ===
    git commit -m "%COMMIT_MSG%"
) else (
    echo Khong co thay doi moi de commit.
)

REM --- Dam bao dang o nhanh main ---
git branch -M main

REM --- Push len GitHub ---
echo.
echo === Dang push len GitHub (co the yeu cau dang nhap / Personal Access Token)... ===
git push -u origin main

echo.
echo === Hoan tat. ===
pause
