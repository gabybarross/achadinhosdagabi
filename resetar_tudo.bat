@echo off
echo ==========================================
echo   RECRIANDO INSTANCIA (COM VERSAO NOVA)
echo ==========================================
echo.
echo 1. Parando containers...
docker-compose down -v --remove-orphans
docker rm -f evolution_api postgres redis 2>nul

echo.
echo 2. Subindo com a versao nova do WhatsApp...
echo (Isso aplica o CONFIG_SESSION_PHONE_VERSION atualizado)
docker-compose up -d

echo.
echo 3. Aguardando containers iniciarem (30 segundos)...
timeout /t 30 /nobreak

echo.
echo ==========================================
echo   PRONTO! Aguarde mais 30 segundos.
echo   Depois rode: ler_qrcode.bat
echo ==========================================
pause
