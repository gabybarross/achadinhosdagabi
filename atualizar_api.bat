@echo off
echo ==========================================
echo      ATUALIZANDO EVOLUTION API
echo ==========================================
echo.
echo 1. Parando container antigo 'evolution_api'...
docker stop evolution_api
docker rm evolution_api
echo.
echo 2. Iniciando NOVO container com correcao (Wait...)...
echo Isso pode levar uns 30 segundos.
echo.

docker run --name evolution_api -d --restart=always -p 8080:8080 --network achadinhos_default -e AUTHENTICATION_API_KEY=B89599B75638-410E-A896-749372138BC3 -e ALLOW_API_KEY_AS_PARAMETER=true -e CONFIG_SESSION_PHONE_VERSION=2.3000.1015330666 -e DATABASE_PROVIDER=postgresql -e "DATABASE_CONNECTION_URI=postgresql://postgres:postgres@postgres:5432/evolution?schema=public" -e "DATABASE_URL=postgresql://postgres:postgres@postgres:5432/evolution?schema=public" -v evolution_store:/evolution/store -v evolution_instances:/evolution/instances atendai/evolution-api:latest

echo.
echo ==========================================
echo      ATUALIZACAO CONCLUIDA!
echo ==========================================
echo Agora tente rodar o 'ler_codigo.bat' novamente em 1 minuto.
echo.
pause
