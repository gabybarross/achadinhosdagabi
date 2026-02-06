@echo off
echo ==========================================
echo      CONVERTENDO EXCEL PARA O SITE
echo ==========================================
echo.
python converter_excel_para_site.py
echo.
echo ==========================================
echo      PUBLICANDO NO GITHUB (SITE)
echo ==========================================
echo.
git add ofertas.js
git commit -m "Atualizacao via Excel (Manual)"
git push origin main
echo.
echo ==========================================
echo           PROCESSO FINALIZADO
echo ==========================================
pause
