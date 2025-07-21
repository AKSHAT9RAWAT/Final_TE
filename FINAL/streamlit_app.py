import streamlit as st
import os
import tempfile
import shutil
import json
from PIL import Image

# --- UI Styling ---
st.set_page_config(page_title="Story Trigger Engine", layout="wide")

st.markdown("""
    <style>
    body, .main {
        background-color: #f4f6fa !important;
    }
    .stApp {
        background: linear-gradient(135deg, #e9eef6 0%, #f4f6fa 100%);
    }
    .header-bar {
        background: linear-gradient(90deg, #e0e5ec 0%, #f7f8fa 100%);
        border-radius: 0 0 32px 32px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.07);
        padding: 2em 2em 1em 2em;
        margin-bottom: 2em;
        text-align: center;
    }
    .stCard {
        background: #fff;
        border-radius: 28px;
        box-shadow: 0 6px 32px rgba(0,0,0,0.09);
        padding: 2.5em 2em 1.5em 2em;
        margin-bottom: 2.5em;
        transition: box-shadow 0.2s;
    }
    .stCard:hover {
        box-shadow: 0 12px 40px rgba(0,0,0,0.13);
    }
    .caption {
        color: #1a73e8;
        font-size: 1.15em;
        font-weight: 500;
        margin-bottom: 0.5em;
        letter-spacing: 0.01em;
    }
    .meaningful-badge {
        display: inline-block;
        padding: 0.4em 1.2em;
        border-radius: 16px;
        font-size: 1.1em;
        font-weight: 600;
        margin: 0.5em 0;
        background: linear-gradient(90deg, #e0ffe0 0%, #b2f2bb 100%);
        color: #1b5e20;
        box-shadow: 0 2px 8px rgba(56,142,60,0.07);
    }
    .not-meaningful-badge {
        display: inline-block;
        padding: 0.4em 1.2em;
        border-radius: 16px;
        font-size: 1.1em;
        font-weight: 600;
        margin: 0.5em 0;
        background: linear-gradient(90deg, #ffe0e0 0%, #ffb2b2 100%);
        color: #b71c1c;
        box-shadow: 0 2px 8px rgba(183,28,28,0.07);
    }
    .notification {
        color: #ff9800;
        font-size: 1.1em;
        margin-top: 0.5em;
        font-weight: 500;
    }
    .divider {
        border-top: 2px solid #e0e5ec;
        margin: 2em 0 2em 0;
    }
    .upload-area {
        border: 2px dashed #b0b8c1;
        border-radius: 24px;
        background: #f7f8fa;
        padding: 2em;
        margin-bottom: 2em;
        text-align: center;
        transition: border 0.2s;
    }
    .upload-area:hover {
        border: 2px solid #1a73e8;
        background: #e3f0ff;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-bar"><h1 style="margin-bottom:0.2em;">📱 Story Trigger Engine</h1><div style="font-size:1.2em;color:#555;">Samsung One UI Inspired</div></div>', unsafe_allow_html=True)

st.markdown('<div class="upload-area">', unsafe_allow_html=True)
st.write("**Upload a set of images (album) and get meaningfulness, captions, and notifications.**")

uploaded_files = st.file_uploader(
    "Select multiple images (album)",
    type=["jpg", "jpeg", "png", "bmp"],
    accept_multiple_files=True,
    help="Upload a set of images to analyze."
)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

if uploaded_files:
    # Save images to a temp album folder
    with tempfile.TemporaryDirectory() as temp_dir:
        album_name = "user_album"
        album_path = os.path.join(temp_dir, album_name)
        os.makedirs(album_path, exist_ok=True)
        for file in uploaded_files:
            img = Image.open(file)
            img.save(os.path.join(album_path, file.name))

        # Prepare FINAL/temp_input/user_album
        final_dir = os.path.abspath("FINAL")
        temp_input = os.path.join(final_dir, "temp_input")
        if os.path.exists(temp_input):
            shutil.rmtree(temp_input)
        os.makedirs(temp_input, exist_ok=True)
        shutil.copytree(album_path, os.path.join(temp_input, album_name))

        # Run BLIP captioning
        os.environ["BASE_FOLDER"] = temp_input
        os.environ["OUTPUT_FOLDER"] = final_dir
        os.environ["BATCH_SIZE"] = "1"
        with st.spinner("Running BLIP captioning..."):
            os.system(f"python {os.path.join(final_dir, 'caption.py')}")

        # Convert cluster captions to trigger input
        cluster_json = os.path.join(final_dir, "cluster_captions_batch_1.json")
        trigger_input_json = os.path.join(final_dir, "trigger_input.json")
        def convert_cluster_to_trigger_input(cluster_json, trigger_input_json):
            with open(cluster_json, "r") as f:
                clusters = json.load(f)
            trigger_input = {album: {"captions": captions} for album, captions in clusters.items()}
            with open(trigger_input_json, "w") as f:
                json.dump(trigger_input, f, indent=2)
        convert_cluster_to_trigger_input(cluster_json, trigger_input_json)

        # Run trigger model
        os.environ["INPUT_PATH"] = trigger_input_json
        os.environ["OUTPUT_PATH"] = os.path.join(final_dir, "trigger_output.json")
        with st.spinner("Running trigger model..."):
            os.system(f"python {os.path.join(final_dir, 'glove_infer.py')}")

        # Run notification
        trigger_output_json = os.path.join(final_dir, "trigger_output.json")
        notification_output_json = os.path.join(final_dir, "notification_output.json")
        with st.spinner("Generating notifications..."):
            os.system(f"python {os.path.join(final_dir, 'notification.py')} {trigger_output_json} {notification_output_json}")

        # Display results
        st.subheader("Results for your album:")
        with open(trigger_output_json, "r") as f:
            trigger_results = json.load(f)
        with open(notification_output_json, "r") as f:
            notifications = json.load(f)

        for album_id, result in trigger_results.items():
            with st.container():
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                st.write(f"<span style='font-size:1.15em;font-weight:600;'>📁 Album:</span> <span style='font-size:1.1em;'>{album_id}</span>", unsafe_allow_html=True)
                img_files = [os.path.join(album_path, img) for img in os.listdir(album_path)]
                cols = st.columns(len(img_files))
                for i, img_file in enumerate(img_files):
                    with cols[i]:
                        st.image(img_file, width=110)
                st.markdown(f'<div class="caption">📝 Caption(s):<br> ' + '<br>'.join(result["captions"]) + '</div>', unsafe_allow_html=True)
                if result["label"] == 1:
                    st.markdown('<span class="meaningful-badge">Meaningful: Yes</span>', unsafe_allow_html=True)
                    notif = notifications.get(album_id, {})
                    st.markdown(f'<div class="notification">🔔 Notification: {notif.get("notification_prompt", "-")}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="not-meaningful-badge">Meaningful: No</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True) 