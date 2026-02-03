@echo off
echo --- ATUALIZANDO SITE ACHADINHOS ---

echo 1. Gerando JSON atualizado...
python gerar_site.py

echo.
echo 2. Enviando para o GitHub...
git add ofertas.js
git commit -m "Atualizacao diaria de ofertas"
git push origin main

echo.
echo --- SUCESSO! O site estara no ar em instantes. ---
pause
