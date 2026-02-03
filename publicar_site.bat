@echo off
echo --- ATUALIZANDO SITE ACHADINHOS ---

echo 1. Buscando ofertas e atualizando o site...
python main.py

echo.
echo 2. Enviando para o GitHub...
git add ofertas.js
git commit -m "Atualizacao diaria de ofertas"
git push origin main

echo.
echo --- SUCESSO! O site estara no ar em instantes. ---
pause
