@echo off
echo Limpiando directorios anteriores...
rmdir /s /q build
rmdir /s /q dist
rmdir /s /q Output

echo Instalando dependencias...
pip install -r requirements.txt

echo Creando ejecutable con PyInstaller...
python -m PyInstaller app.spec

echo Creando instalador con Inno Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss

echo Instalador creado en la carpeta Output
pause

