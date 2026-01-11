import gradio as gr
import utils.youtube_fetcher as yt
import time
import random
import traceback
import os
import yt_dlp
import scipy.io.wavfile
from engine import matcher
from core import fingerprinter

from database import db_handler

def identify_from_youtube(url):
    if not url:
        return "Please paste a URL first."

    try:
        # fetch metadata
        song_data = yt.get_song_info_from_youtube(url)
        
        if not song_data:
            return "Error: Could not fetch data from YouTube."

        # unpack metadata
        title, artist, duration, thumbnail, yt_url = song_data

        # options to download audio for training
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'temp_train.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'wav',}],
            'quiet': True,
        }

        # download audio to temp file
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # save song to db
        song_id = db_handler.add_song(title, artist, duration, thumbnail, yt_url)
        
        if song_id:
            # process audio to generate hashes
            hashes = fingerprinter.process_audio("temp_train.wav")
            
            # prepare data for batch insert
            batch_data = [(h, song_id, o) for h, o in hashes]
            
            # fast insert
            db_handler.add_hashes_batch(batch_data)

            # cleanup temp file
            if os.path.exists("temp_train.wav"):
                os.remove("temp_train.wav")

            return f"SUCCESS! Saved to DB:\nTitle: {title}\nArtist: {artist}\nID: {song_id}\nHashes: {len(hashes)}"
        else:
            return "Error: Database save failed."

    except Exception as e:
        return f"Error: {traceback.format_exc()}"
    
def load_library_view():
    try:
        songs = db_handler.get_all_songs()
        
        if not songs:
            return "<h3 style='color: white; text-align: center;'>Library is empty. Train some songs first!</h3>"
        
        html_output = ""
        for s in songs:
            # s is tuple (name, artist, duration, thumbnail_url)
            html_output += create_list_style_card(s[3], s[0], s[1], s[2])
            
        return html_output
    except Exception as e:
        return f"<p style='color: red;'>Error loading library: {str(e)}</p>"

def process_identification(audio, history_list):
    if audio is None:
        gr.Warning("You need to record something before trying to Identify it!")
        return gr.update(), gr.update(), gr.update(), gr.update(), history_list, gr.update()

    # unpack gradio audio (rate, data)
    rate, data = audio
    
    # save temp wav file for processing
    scipy.io.wavfile.write("temp_rec.wav", rate, data)
    
    # identify song using matcher
    data = matcher.identify_song("temp_rec.wav")
    
    # cleanup recording
    if os.path.exists("temp_rec.wav"):
        os.remove("temp_rec.wav")

    # check if match found
    if not data:
        gr.Warning("No match found in library.")
        return gr.update(), gr.update(visible=True), gr.update(visible=False), gr.update(), history_list, gr.update()

    # create apple style card
    apple_card_html = create_music_card(data["img"], data["title"], data["artist"], data["dur"])

    # update history
    history_list.insert(0, data)
    
    # regenerate history html
    history_html_content = ""
    for song in history_list:
        history_html_content += create_list_style_card(song["img"], song["title"], song["artist"], song["dur"])

    # return updated ui elements
    return (
        apple_card_html,           
        gr.update(visible=False),  
        gr.update(visible=True),   
        history_html_content,      
        history_list,         
        gr.update(link=data["url"], visible=True)
    )

def close_overlay():
    # back button action
    return gr.update(visible=True), gr.update(visible=False)

def create_list_style_card(thumbnail_url, title, artist, duration):
    if not thumbnail_url:
        thumbnail_url = "https://cdn-icons-png.flaticon.com/512/461/461238.png"

    html_content = f"""
    <div style="
        display: flex; 
        align-items: center; 
        background-color: #1f2937; 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid #10b981; 
        margin-bottom: 12px; 
        color: white;
        font-family: sans-serif;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    ">
        <div style="flex-shrink: 0;">
            <img src="{thumbnail_url}" 
                 style="width: 70px; height: 70px; object-fit: cover; border-radius: 8px; margin-right: 15px; display: block;" 
                 alt="Art">
        </div>
        <div style="display: flex; flex-direction: column; justify-content: center;">
            <h4 style="margin: 0; font-size: 18px; font-weight: bold;">{title}</h4>
            <p style="margin: 0; font-size: 15px; color: #10b981;">{artist}</p> <p style="margin: 0; font-size: 12px; color: #9ca3af;">⏱ {duration}s</p>
        </div>
    </div>
    """
    return html_content

def create_music_card(thumbnail_url, title, artist, duration):
    if not thumbnail_url:
        thumbnail_url = "https://cdn-icons-png.flaticon.com/512/461/461238.png"

    html_content = f"""
    <div style="
        display: flex; 
        flex-direction: column;
        align-items: center; 
        text-align: center;
        background-color: #1f2937; 
        padding: 40px 40px 20px 40px; 
        border-radius: 24px 24px 0 0;
        border: 1px solid #374151;
        border-bottom: none;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        width: 100%;
        color: white;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    ">
        <img src="{thumbnail_url}" 
             style="width: 300px; height: 300px; object-fit: cover; border-radius: 16px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.4);" 
             alt="Album Art">
        
        <h2 style="margin: 0 0 10px 0; font-size: 28px; font-weight: bold;">{title}</h2>
        <h3 style="margin: 0 0 20px 0; font-size: 20px; color: #10b981; font-weight: 600;">{artist}</h3> <p style="margin: 0; font-size: 14px; color: #9ca3af; letter-spacing: 1px; font-weight: bold;">DURATION: {duration}s</p>
    </div>
    """
    return html_content

with gr.Blocks(
    title="PyTone",
    theme=gr.themes.Default(
        primary_hue=gr.themes.colors.green,
        secondary_hue=gr.themes.colors.emerald,
        neutral_hue=gr.themes.colors.gray,
    )
) as ui_layout:
    # env variable
    history_state = gr.State([])
    # title
    gr.Markdown("# PyTone")
    # subtitle
    gr.Markdown("## _That_ song. One tap away.")

    # the 2 main tabs
    with gr.Tabs():
        # training tab
        with gr.Tab("Train a new song"):
            youtube_url = gr.Textbox(
                label="Paste the Youtube URL of the song you want to use for training:",
                placeholder="https://www.youtube.com/watch?v=..."
            )
            youtube_button = gr.Button("Load the song")
            youtube_output = gr.Textbox(label="Result", lines=6)

            youtube_button.click(
                identify_from_youtube,
                inputs=youtube_url,
                outputs=youtube_output
            )

        # identification tab
        with gr.Tab("Identify an existing song"):

            with gr.Column(visible=True) as input_container:
                mic_input = gr.Audio(
                    sources=["microphone"],
                    type="numpy",
                    label="Listen"
                )
                listen_btn = gr.Button(
                    "Identify",
                    variant="primary",
                    size="lg"
                )
            
            with gr.Column(visible=False) as result_container:
                gr.HTML("<br>")

                with gr.Row():

                    with gr.Column(scale=1):
                        pass

                    with gr.Column(scale=0, min_width=500):
                        result_card = gr.HTML(label="Identified Song", padding=False)

                        with gr.Row():
                            back_btn = gr.Button(
                                "Search Another",
                                variant="primary",
                                size="lg"
                            )

                            redirect_btn = gr.Button(
                                "View on YouTube",
                                variant="secondary",
                                size="lg"
                            )
                    
                    with gr.Column(scale=1):
                        pass

        with gr.Tab("History"):
            gr.Markdown("Previously Identified Songs")
            history_output = gr.HTML("No songs identified yet.")

        with gr.Tab("Library"):
            gr.Markdown("### Song Library")
            refresh_lib_btn = gr.Button("Refresh", size="sm")

            library_output = gr.HTML(value=load_library_view)

            refresh_lib_btn.click(
                fn=load_library_view,
                inputs=[],
                outputs=library_output
            )

    listen_btn.click(
        fn = process_identification,
        inputs=[mic_input, history_state],
        outputs=[
            result_card,
            input_container,
            result_container,
            history_output,
            history_state,
            redirect_btn
        ]
    )

    back_btn.click(
        fn=close_overlay,
        inputs=[],
        outputs=[input_container, result_container]
    )