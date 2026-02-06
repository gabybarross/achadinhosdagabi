@echo off
title Robô de Envio WhatsApp (Automático)
echo ==========================================
echo      INICIANDO ROBO WHATSAPP
echo ==========================================
echo.
echo Este robo vai:
echo 1. Ler o arquivo Excel (ofertas_para_site.xlsx)
echo 2. Pegar 2 produtos que voce marcou com 'x'
echo 3. Agrupar para nao repetir itens iguais
echo 4. Enviar e esperar 1 hora para o proximo lote
echo.
python bot_whatsapp.py
pause
