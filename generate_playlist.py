import os
from datetime import datetime, timedelta

BASE_PLAYLIST = "playlist_base.m3u"
ARCHIVE_DIR = "archive"
OUTPUT_PLAYLIST = "playlist.m3u"
DAYS_TO_KEEP = 3

os.makedirs(ARCHIVE_DIR, exist_ok=True)

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def archive_today_playlist():
    today = datetime.now().strftime("%Y-%m-%d")
    archive_path = os.path.join(ARCHIVE_DIR, f"playlist-{today}.m3u")
    if not os.path.exists(archive_path):
        print(f"Archivieren: {archive_path}")
        content = read_file(BASE_PLAYLIST)
        write_file(archive_path, content)

def cleanup_old_archives():
    cutoff = datetime.now() - timedelta(days=DAYS_TO_KEEP)
    for filename in os.listdir(ARCHIVE_DIR):
        if filename.startswith("playlist-") and filename.endswith(".m3u"):
            date_str = filename[len("playlist-"):-len(".m3u")]
            try:
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date < cutoff:
                    print(f"Entferne alte Datei: {filename}")
                    os.remove(os.path.join(ARCHIVE_DIR, filename))
            except ValueError:
                pass

def build_combined_playlist():
    combined = "#EXTM3U\n"
    # Optional: EPG URL einfügen
    combined += 'x-tvg-url="https://epg.teleguide.info/ru/epg.xml"\n'
    
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(DAYS_TO_KEEP)]
    for date_str in dates:
        path = os.path.join(ARCHIVE_DIR, f"playlist-{date_str}.m3u")
        if os.path.exists(path):
            content = read_file(path)
            lines = [line for line in content.splitlines() if not line.startswith("#EXTM3U")]
            combined += f"\n# Archiv vom {date_str}\n"
            combined += "\n".join(lines) + "\n"
    write_file(OUTPUT_PLAYLIST, combined)
    print(f"Erstellt kombinierte Playlist: {OUTPUT_PLAYLIST}")

if __name__ == "__main__":
    archive_today_playlist()
    cleanup_old_archives()
    build_combined_playlist()
