#!/usr/bin/env python3
import os
import re
import sys
import yt_dlp

MUSIC_DIR = os.environ.get("SLOPIFY_DIR", os.path.expanduser("~/storage/music/slopify"))
PLAYLISTS_DIR = os.path.join(MUSIC_DIR, "_playlists")

RADIO_COUNT = 30


def base_opts(collected_files=None):
    opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(
            MUSIC_DIR, "%(artist,channel)s/%(album,NA)s/%(title)s.%(ext)s"
        ),
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "m4a"},
            {"key": "FFmpegMetadata", "add_metadata": True},
        ],
        "ignoreerrors": True,
    }
    if collected_files is not None:
        opts["progress_hooks"] = [_make_file_collector(collected_files)]
    return opts


def _make_file_collector(collected):
    def hook(d):
        if d["status"] == "finished":
            collected.append(d["filename"])
    return hook


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def get_song(query):
    with yt_dlp.YoutubeDL(base_opts()) as ydl:
        ydl.download([f"ytsearch1:{query}"])


def get_album(query):
    search_opts = {"quiet": True, "extract_flat": True}
    with yt_dlp.YoutubeDL(search_opts) as ydl:
        info = ydl.extract_info(f"ytsearch5:{query} album", download=False)

    album_url = None
    for entry in info.get("entries") or []:
        url = entry.get("url", "")
        if "list=" in url or entry.get("_type") == "playlist":
            album_url = url
            break

    if not album_url:
        print(f"No album playlist found for: {query}")
        print("Tip: try 'artist album_name' e.g. 'metallica master of puppets'")
        return

    with yt_dlp.YoutubeDL(base_opts()) as ydl:
        ydl.download([album_url])


def get_radio(query, count=RADIO_COUNT):
    search_opts = {"quiet": True, "extract_flat": True}
    with yt_dlp.YoutubeDL(search_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=False)

    entries = (info.get("entries") or [])
    if not entries:
        print(f"No seed song found for: {query}")
        return

    video_id = entries[0]["id"]
    radio_url = f"https://music.youtube.com/watch?v={video_id}&list=RDAMVM{video_id}"

    downloaded = []
    opts = base_opts(collected_files=downloaded)
    opts["playlistend"] = count
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([radio_url])

    if downloaded:
        _write_m3u(query, downloaded)


def _write_m3u(name, files):
    os.makedirs(PLAYLISTS_DIR, exist_ok=True)
    playlist_path = os.path.join(PLAYLISTS_DIR, f"{_slug(name)}.m3u")
    with open(playlist_path, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for path in files:
            # progress hook gives .webm/.part before postprocessor renames to .m4a
            m4a = os.path.splitext(path)[0] + ".m4a"
            f.write(m4a + "\n")
    print(f"Playlist saved: {playlist_path}")


COMMANDS = {"s": get_song, "a": get_album, "r": get_radio}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: slopify <s|a|r> <query>")
        print("  s master of puppets")
        print("  a chocolate starfish")
        print("  r prodigy breathe")
        sys.exit(1)

    cmd = sys.argv[1]
    query = " ".join(sys.argv[2:])

    if cmd not in COMMANDS:
        print(f"Unknown command '{cmd}'. Use s (song), a (album), r (radio).")
        sys.exit(1)

    COMMANDS[cmd](query)
