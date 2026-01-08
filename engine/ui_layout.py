import gradio as gr

def identify_from_spotify(url):
    return f"Loaded Spotify track: {url}"

def identify_from_mic(audio):
    return "Identified song from microphone input"

with gr.Blocks(title="PyTone") as ui_layout:
    # title
    gr.Markdown("# PyTone")
    # subtitle
    gr.Markdown("## _That_ song. One tap away.")

    # the 2 main tabs
    with gr.Tabs():
        # training tab
        with gr.Tab("Train a new song"):
            spotify_url = gr.Textbox(
                label="Paste the Spotify URL of the song you want to use for training:",
                placeholder="https://open.spotify.com/track/..."
            )
            spotify_btn = gr.Button("Load the track")
            spotify_output = gr.Textbox(label="Result")

            spotify_btn.click(
                identify_from_spotify,
                inputs=spotify_url,
                outputs=spotify_output
            )

        # identification tab
        with gr.Tab("Identify an existing song"):
            mic_input = gr.Audio(
                sources=["microphone"],
                type="numpy",
                label="Listen"
            )
            listen_btn = gr.Button("Identify")
            listen_output = gr.Textbox(label="Result")

            listen_btn.click(
                identify_from_mic,
                inputs=mic_input,
                outputs=listen_output
            )

# launch ui
ui_layout.launch(
    # ui theme
    theme=gr.themes.Default(
        primary_hue=gr.themes.colors.green,
        secondary_hue=gr.themes.colors.emerald,
        neutral_hue=gr.themes.colors.gray,
    )
)