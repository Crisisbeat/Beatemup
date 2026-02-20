@echo off
echo ==========================================
echo    Limpiando y Subiendo a GitHub
echo ==========================================

echo Paso 1: Quitando archivos pesados de la lista...
git rm -r --cached . >nul 2>&1

echo Paso 2: Volviendo a preparar solo lo necesario...
git add .

echo Paso 3: Guardando cambios limpios...
git commit -m "Limpiando archivos pesados (PSD/AVI) para GitHub"

echo Paso 4: Subiendo (esto sera mas rapido ahora)...
git push -u origin main --force

echo.
echo ==============================================
echo   ¡INTENTO 2 COMPLETADO!
echo ==============================================
echo Ve a: https://github.com/Crisisbeat/Beatemup/actions
echo.
pause
