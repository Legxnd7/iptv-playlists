Param(
    [string]$streamUrl,
    [string]$slug,
    [int]$duration = 7200,
    [string]$outRoot = "C:\Users\Oliver\Desktop\IPTV-Archiv"
)
# record_once.ps1 - records a stream using ffmpeg (Windows)
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) { 
    Write-Error "ffmpeg not found in PATH. Please install ffmpeg and add to PATH."
    exit 2
}
$outDir = Join-Path $outRoot $slug
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
$outFile = Join-Path $outDir ($slug + "-" + (Get-Date -Format yyyy-MM-dd) + ".mp4")
Write-Output "Recording $streamUrl -> $outFile for $duration seconds"
# ffmpeg recording. -t $duration sets recording length in seconds.
& ffmpeg -hide_banner -loglevel warning -y -i $streamUrl -c copy -t $duration $outFile
# cleanup older than 3 days
Get-ChildItem -Path $outDir -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-3) } | Remove-Item -Force -Verbose
Write-Output "Done recording: $outFile"
