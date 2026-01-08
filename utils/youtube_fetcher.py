import yt_dlp

def get_song_info_from_youtube(url):
    # suppress output and skip download
    ydl_opts = {'quiet': True, 'noplaylist': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # fetch direct url, removed search wrapper and list index
        info = ydl.extract_info(url, download=False)
        return info['title'], info['uploader'], info['duration']