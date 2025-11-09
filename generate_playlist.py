import os
from datetime import datetime, timedelta

BASE_PLAYLIST = "playlist_base.m3u"
ARCHIVE_DIR = "archive"
OUTPUT_PLAYLIST = "playlist.m3u"
DAYS_TO_KEEP = 3

# Liste deiner Kanäle mit ihren tvg-ids (muss zu playlist_base passen)
CHANNELS = [
    "ntv",
    "russia1",
    "tnt",
    "erste",
    "sts"
]

os.makedirs(ARCHIVE_DIR, exist_ok=True)

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def extract_channel_entries(base_content, channel_id):
    """
    Extrahiert alle EXTINF- und Stream-Zeilen für einen Kanal aus der Basis-Playlist
    """
    lines = base_content.splitlines()
    entries = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF") and f'tvg-id="{channel_id}"' in line:
            entries.append(line)
            # Nächste Zeile ist die Stream-URL
            if i + 1 < len(lines):
                entries.append(lines[i + 1])
            i += 2
        else:
            i += 1
    return "\n".join(entries)

def archive_playlists():
    base_content = read_file(BASE_PLAYLIST)
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Für jeden Kanal eine Archivdatei heute erstellen, wenn noch nicht vorhanden
    for channel in CHANNELS:
        archive_path = os.path.join(ARCHIVE_DIR, f"{channel}-{today}.m3u")
        if not os.path.exists(archive_path):
            print(f"Erstelle Archiv für {channel}: {archive_path}")
            entries = extract_channel_entries(base_content, channel)
            content = "#EXTM3U\n" + entries + "\n"
            write_file(archive_path, content)

def cleanup_old_archives():
    cutoff = datetime.now() - timedelta(days=DAYS_TO_KEEP)
    for filename in os.listdir(ARCHIVE_DIR):
        if any(filename.startswith(ch) for ch in CHANNELS) and filename.endswith(".m3u"):
            date_str = filename.split("-")[-1].replace(".m3u", "")
            try:
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date < cutoff:
                    print(f"Entferne alte Archivdatei: {filename}")
                    os.remove(os.path.join(ARCHIVE_DIR, filename))
            except ValueError:
                pass

def build_combined_playlist():
    combined = "#EXTM3U\n"
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(DAYS_TO_KEEP)]
    base_content = read_file(BASE_PLAYLIST)
    
    # Füge Live-Streams aus Basis hinzu (ohne Catchup-Attribute)
    lines = base_content.splitlines()
    live_lines = []
    for line in lines:
        if line.startswith("#EXTINF") or line.startswith("http"):
            # Entferne catchup Attribute für Live Playlist
            line = line.replace(' catchup="default"', '')
            line = line.replace(' catchup-days="3"', '')
            # Entferne catchup-source falls vorhanden
            parts = line.split(' catchup-source=')
            line = parts[0]
            live_lines.append(line)
        else:
            # Nur #EXTM3U ignorieren, sonst hinzufügen
            if not line.startswith("#EXTM3U"):
                live_lines.append(line)
    combined += "\n".join(live_lines) + "\n\n"

    # Füge Archivdateien (letzte Tage) als Kommentare hinzu (optional)
    for date_str in dates:
        combined += f"# Playlist-Archiv vom {date_str}\n"
        for channel in CHANNELS:
            archive_path = os.path.join(ARCHIVE_DIR, f"{channel}-{date_str}.m3u")
            if os.path.exists(archive_path):
                content = read_file(archive_path)
                # Header entfernen, sonst Doppelte #EXTM3U
                content_lines = content.splitlines()
                content_lines = [l for l in content_lines if not l.startswith("#EXTM3U")]
                combined += "\n".join(content_lines) + "\n"
        combined += "\n"
    write_file(OUTPUT_PLAYLIST, combined)
    print(f"Kombinierte Playlist erstellt: {OUTPUT_PLAYLIST}")

if __name__ == "__main__":
    archive_playlists()
    cleanup_old_archives()
    build_combined_playlist()
