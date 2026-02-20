@echo off
echo ==========================================
echo    Beat 'em Up 2.5D Prototype
echo ==========================================
echo Verificando dependencias...
pip install pygame-ce pillow --quiet
if %errorlevel% neq 0 (
    echo Intentando instalar pygame estandar y pillow...
    pip install pygame pillow --quiet
)

echo.
echo CONTROLES:
echo - FLECHAS: Movimiento (Double Tap Derecha para Dash)
echo - Z: Ataque (Combo de 4 golpes)
echo - X: Ataque Especial (Gira y gasta vida)
echo - ESPACIO: Salto
echo - ESPACIO (en el aire): Dive Attack
echo.
echo Cargando demo...
python main.py
pause
