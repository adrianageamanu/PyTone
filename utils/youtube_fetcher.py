import yt_dlp

def get_song_info_from_youtube(url):
    # suppress output and skip download
    ydl_options = {
        'quiet': True, 
        'noplaylist': True,

        # best audio quality
        'format': 'bestaudio/best',
    }

    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        # fetch direct url, no download
        info = ydl.extract_info(url, download=True)
        return (
            info['title'], 
            info['uploader'], 
            info['duration'],

            # fetch thumbnail url
            info['thumbnail_url'],

            # fetch audio url
            info['audio_url']
        )