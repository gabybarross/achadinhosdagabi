@echo off
cd /d "d:\04_APPs\Achadinhos"
echo --- ATUALIZANDO SITE ACHADINHOS ---

echo 1. Buscando ofertas e atualizando o site (main.py)...
python main.py

echo.
echo 2. Enviando atualizacoes para o GitHub...
git add ofertas.js banco_ofertas_completo.csv
git commit -m "Atualizacao rapida (Manual)"
git push origin main

echo.
echo --- SUCESSO! O site foi atualizado (Modo Rapido). ---
pause
