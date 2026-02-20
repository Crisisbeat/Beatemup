@echo off
echo ==========================================
echo    Subiendo Beat 'em Up a GitHub
echo ==========================================

:: Verificar si git esta instalado
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git no esta instalado en tu PC.
    echo Por favor instala Git desde https://git-scm.com/
    pause
    exit
)

echo Preparando archivos...
git add .

echo Guardando cambios...
git commit -m "Configuracion de APK automatica"

echo Conectando con el repositorio de Crisisbeat...
git branch -M main
:: Intentamos remover el origin por si ya existia uno previo
git remote remove origin >nul 2>&1
git remote add origin https://github.com/Crisisbeat/Beatemup.git

echo Enviando a la nube (GitHub)...
echo SI SE ABRE UNA VENTANA DE NAVEGADOR, POR FAVOR INICIA SESIÓN.
git push -u origin main

echo.
echo ==============================================
echo   ¡PROCESO COMPLETADO!
echo ==============================================
echo Ahora ve a: https://github.com/Crisisbeat/Beatemup/actions
echo Espera unos minutos a que el robot termine de fabricar tu APK.
echo.
pause
