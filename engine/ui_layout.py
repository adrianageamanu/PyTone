import gradio as gr
import utils.youtube_fetcher as yt

def identify_from_youtube(url):
    return f"Loaded Youtube song: {yt.get_song_info_from_youtube(url)}"

def identify_from_mic(audio):
    return "Identified song from microphone input"

with gr.Blocks(
    title="PyTone",
    theme=gr.themes.Default(
        primary_hue=gr.themes.colors.green,
        secondary_hue=gr.themes.colors.emerald,
        neutral_hue=gr.themes.colors.gray,
    )
) as ui_layout:
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