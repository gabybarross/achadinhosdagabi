@echo off
echo ==========================================
echo      REINSTALANDO TUDO (DO ZERO)
echo ==========================================
echo.
echo 1. Derrubando containers E VOLUMES antigos (Limpeza Total)...
docker-compose down -v --remove-orphans
docker rm -f evolution_api postgres redis 2>nul

echo.
echo 2. Subindo ambiente novo...
echo Isso pode levar um tempinho (baixando imagens se precisar)...
docker-compose up -d

echo.
echo ==========================================
echo      PRONTO! AMBIENTE NOVO NO AR.
echo ==========================================
echo Aguarde uns 60 segundos antes de conectar.
pause
