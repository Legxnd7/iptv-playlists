Param(
    [string]$streamUrl,
    [string]$slug,
    [int]$duration = 7200,
    [string]$outRoot = "C:\Users\Oliver\Desktop\IPTV-Archiv"
)
# Prüfen ob ffmpeg vorhanden
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Error "ffmpeg nicht gefunden. Bitte ffmpeg installieren und in PATH einfügen."
    exit 2
}
# Ordner anlegen
$outDir = Join-Path $outRoot $slug
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
# Datei-Timestamp: eine Datei pro Tag (vereinfachte Variante)
$outFile = Join-Path $outDir ($slug + "-" + (Get-Date -Format yyyy-MM-dd) + ".m3u")
# Wir schreiben eine m3u, kein großes Video (Option 1: m3u-Catchup). 
# Falls du echte mp4-Aufnahme willst: passe ffmpeg-Befehl unten an.
$content = "#EXTM3U`n#EXTINF:-1,$slug - Archive `n$streamUrl"
Set-Content -Path $outFile -Value $content -Encoding UTF8

Write-Output "Erstellt M3U-Catchup-Eintrag: $outFile"

# Alte Einträge prüfen und löschen (älter als 3 Tage)
Get-ChildItem -Path $outDir -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-3) } | Remove-Item -Force -Verbose
Write-Output "Aufräumen abgeschlossen für: $outDir"
