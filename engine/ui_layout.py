import gradio as gr
import utils.youtube_fetcher as yt
import time
import random

def identify_from_youtube(url):
    return f"Loaded Youtube song: {yt.get_song_info_from_youtube(url)}"

def process_identification(audio, history_list):
    """
    Această funcție face 4 lucruri:
    1. Simulează identificarea.
    2. Generează cardul Apple (pentru vizualizare).
    3. Actualizează istoricul (adaugă melodia în listă).
    4. Schimbă vizibilitatea (ascunde microfonul, arată rezultatul).
    """
    if audio is None:
        # Nu schimbăm nimic dacă nu e audio, doar returnăm un mesaj de eroare sau null
        # Pentru simplitate, returnăm starea curentă neschimbată
        return gr.update(), gr.update(), gr.update(), gr.update(), history_list

    # Simulare procesare
    time.sleep(1.5)
    
    # --- DUMMY DATA ---
    # Putem randomiza puțin titlul ca să vedem că merge istoricul
    import random
    songs = [
        {"title": "Bohemian Rhapsody", "artist": "Queen", "dur": 354, "img": "https://upload.wikimedia.org/wikipedia/en/9/9f/Bohemian_Rhapsody.png"},
        {"title": "Billie Jean", "artist": "Michael Jackson", "dur": 294, "img": "https://upload.wikimedia.org/wikipedia/en/5/55/Michael_Jackson_-_Billie_Jean.jpg"},
        {"title": "Shape of You", "artist": "Ed Sheeran", "dur": 233, "img": "https://upload.wikimedia.org/wikipedia/en/b/b4/Shape_Of_You_%28Official_Single_Cover%29.png"}
    ]
    data = random.choice(songs)

    # 1. Creăm HTML-ul pentru cardul mare (Apple style)
    apple_card_html = create_music_card(data["img"], data["title"], data["artist"], data["dur"])

    # 2. Actualizăm Istoricul
    # Adăugăm noua melodie la începutul listei
    history_list.insert(0, data)
    
    # Regenerăm HTML-ul pentru tot istoricul
    history_html_content = ""
    for song in history_list:
        history_html_content += create_list_style_card(song["img"], song["title"], song["artist"], song["dur"])

    # 3. Returnăm tot
    return (
        apple_card_html,           # Output pentru Result Card
        gr.update(visible=False),  # Input Container -> Ascuns
        gr.update(visible=True),   # Result Container -> Vizibil
        history_html_content,      # Output pentru History Tab
        history_list               # Actualizăm variabila de stare (State)
    )

def close_overlay():
    """Funcție simplă care resetează vizualizarea (Butonul Back)"""
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
        border-radius: 24px 24px 0 0; /* modificare: colturi rotunjite doar sus pentru continuitate cu butonul */
        border: 1px solid #374151;
        border-bottom: none;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        width: 100%; /* ocupa tot spatiul din containerul parinte */
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
            youtube_output = gr.Textbox(label="Result")

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

                        back_btn = gr.Button(
                            "Search Another",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=1):
                        pass

        with gr.Tab("History"):
            gr.Markdown("Previously Identified Songs")
            history_output = gr.HTML("No songs identified yet.")

    listen_btn.click(
        fn = process_identification,
        inputs=[mic_input, history_state],
        outputs=[
            result_card,
            input_container,
            result_container,
            history_output,
            history_state
        ]
    )

    back_btn.click(
        fn=close_overlay,
        inputs=[],
        outputs=[input_container, result_container]
    )

    