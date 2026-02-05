$ErrorActionPreference = "Stop"

$ffmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$zipPath = "ffmpeg.zip"
$extractPath = "ffmpeg_temp"

Write-Host "Baixando FFmpeg..."
Invoke-WebRequest -Uri $ffmpegUrl -OutFile $zipPath

Write-Host "Extraindo FFmpeg..."
Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

# Encontrar o ffmpeg.exe dentro da pasta extraída (a estrutura interna pode variar)
$ffmpegBinary = Get-ChildItem -Path $extractPath -Recurse -Filter "ffmpeg.exe" | Select-Object -First 1

if ($ffmpegBinary) {
    Copy-Item -Path $ffmpegBinary.FullName -Destination ".\ffmpeg.exe" -Force
    Write-Host "FFmpeg instalado com sucesso em: $(Get-Location)\ffmpeg.exe"
} else {
    Write-Error "Não foi possível encontrar o ffmpeg.exe dentro do arquivo zip."
}

# Limpeza
Write-Host "Limpando arquivos temporários..."
Remove-Item -Path $zipPath -Force
Remove-Item -Path $extractPath -Recurse -Force

Write-Host "Concluído!"
