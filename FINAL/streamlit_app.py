import streamlit as st
import os
import tempfile
import shutil
import json
from PIL import Image
import requests
import time

# --------------- Lottie Loader ---------------

# --------------- App Layout & Config ---------------
st.set_page_config(page_title="Story Trigger Engine", layout="wide")
st.markdown(
    """
    <style>
    .stApp {background: linear-gradient(135deg, #e9eef6 0%, #f4f6fa 100%) !important;}
    </style>
    """,
    unsafe_allow_html=True
)


# ------------- Main UI Area -------------
st.markdown(
    "<h2 style='text-align:center;'>📸 Analyze Your Memories</h2>", unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;font-size:1.1em;color:#666;'>Upload your images below. Supports multiple image selection.</p>",
    unsafe_allow_html=True
)

# --- Session state for workflow ---
if 'analysis_complete' not in st.session_state:
    st.session_state['analysis_complete'] = False
if 'album_path' not in st.session_state:
    st.session_state['album_path'] = None
if 'trigger_output_json' not in st.session_state:
    st.session_state['trigger_output_json'] = None
if 'notification_output_json' not in st.session_state:
    st.session_state['notification_output_json'] = None
if 'uploader_key' not in st.session_state:
    st.session_state['uploader_key'] = 0

# --- Clear All Button ---
def clear_all():
    # Remove persistent album and outputs
    final_dir = os.path.abspath("FINAL")
    temp_input = os.path.join(final_dir, "temp_input")
    try:
        if os.path.exists(temp_input):
            shutil.rmtree(temp_input)
        for f in ["trigger_output.json", "notification_output.json", "trigger_input.json", "cluster_captions_batch_1.json", "image_captions_batch_1.json"]:
            fp = os.path.join(final_dir, f)
            if os.path.exists(fp):
                os.remove(fp)
    except Exception as e:
        pass
    st.session_state['analysis_complete'] = False
    st.session_state['album_path'] = None
    st.session_state['trigger_output_json'] = None
    st.session_state['notification_output_json'] = None
    st.session_state['uploader_key'] += 1
    st.rerun()

st.divider()

uploaded_files = st.file_uploader(
    "Select multiple images (album)",
    type=["jpg", "jpeg", "png", "bmp"],
    accept_multiple_files=True,
    label_visibility="collapsed",
    help="Upload a set of images to analyze.",
    key=st.session_state['uploader_key']
)

st.divider()

def run_album_analysis(uploaded_files):
    start_time = time.time()
    # Save images to a temp album folder
    with tempfile.TemporaryDirectory() as temp_dir:
        album_name = "user_album"
        album_path = os.path.join(temp_dir, album_name)
        os.makedirs(album_path, exist_ok=True)
        for file in uploaded_files:
            img = Image.open(file)
            # img.thumbnail((384, 384), Image.LANCZOS)  # Downsampling disabled for timing comparison
            img.save(os.path.join(album_path, file.name))

        # Prepare FINAL/temp_input/user_album
        final_dir = os.path.abspath("FINAL")
        temp_input = os.path.join(final_dir, "temp_input")
        if os.path.exists(temp_input):
            shutil.rmtree(temp_input)
        os.makedirs(temp_input, exist_ok=True)
        persistent_album_path = os.path.join(temp_input, album_name)
        shutil.copytree(album_path, persistent_album_path)

        # Run BLIP captioning
        os.environ["BASE_FOLDER"] = temp_input
        os.environ["OUTPUT_FOLDER"] = final_dir
        os.environ["BATCH_SIZE"] = "8"
        with st.spinner("🔄 Running BLIP captioning..."):
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
        with st.spinner("🧠 Running trigger model..."):
            os.system(f"python {os.path.join(final_dir, 'glove_infer.py')}")

        # Run notification
        trigger_output_json = os.path.join(final_dir, "trigger_output.json")
        notification_output_json = os.path.join(final_dir, "notification_output.json")
        with st.spinner("🔔 Generating notifications..."):
            os.system(f"python {os.path.join(final_dir, 'notification.py')} {trigger_output_json} {notification_output_json}")

        # Return persistent album path instead of temp
        total_time = time.time() - start_time
        return persistent_album_path, trigger_output_json, notification_output_json, total_time

# ------------- Main Workflow -------------
if uploaded_files and not st.session_state['analysis_complete']:
    with st.spinner("Processing your album. Please wait... ⏳"):
        album_path, trigger_output_json, notification_output_json, total_time = run_album_analysis(uploaded_files)
        st.session_state['album_path'] = album_path
        st.session_state['trigger_output_json'] = trigger_output_json
        st.session_state['notification_output_json'] = notification_output_json
        st.session_state['total_time'] = total_time
        st.session_state['analysis_complete'] = True
    st.rerun()

if st.session_state['analysis_complete']:
    album_path = st.session_state['album_path']
    trigger_output_json = st.session_state['trigger_output_json']
    notification_output_json = st.session_state['notification_output_json']
    total_time = st.session_state.get('total_time', None)
    st.success("Analysis complete! View your results below.")
    if total_time is not None:
        st.info(f"Total inference time: {total_time:.2f} seconds")

    # Load & show results
    with open(trigger_output_json, "r") as f:
        trigger_results = json.load(f)
    with open(notification_output_json, "r") as f:
        notifications = json.load(f)

    st.markdown("### Your Album Results")

    # For exporting results
    def format_export(trigger, notifications):
        export_res = {}
        for k, v in trigger.items():
            export_res[k] = {
                "captions": v.get("captions"),
                "meaningful": bool(v.get("label")==1),
                "notification": notifications.get(k, {}).get("notification_prompt")
            }
        return json.dumps(export_res, indent=2)

    # Show each album (expandable), images, captions, labels
    for album_id, result in trigger_results.items():
        with st.expander(f"📁 Album: {album_id}", expanded=True):
            img_files = sorted([os.path.join(album_path, img) for img in os.listdir(album_path)])
            cols = st.columns(min(3, len(img_files)))
            for idx, img_file in enumerate(img_files):
                with cols[idx % len(cols)]:
                    st.image(img_file, width=160)
            st.markdown("**Captions:**")
            for cp in result["captions"]:
                st.code(cp, language=None)
            is_meaningful = result["label"] == 1
            color = "#1b5e20" if is_meaningful else "#d32f2f"
            badge = "Yes" if is_meaningful else "No"
            st.markdown(
                f"<span style='display:inline-block;padding:4px 18px;border-radius:13px; "
                f"background:{'#e0ffe0' if is_meaningful else '#ffe0e0'}; "
                f"color:{color};font-weight:600;font-size:1.08em;'>"
                f"Meaningful: {badge}</span>",
                unsafe_allow_html=True
            )
            if is_meaningful:
                notif = notifications.get(album_id, {})
                st.info(f"🔔 Notification: {notif.get('notification_prompt', '-')}")
    st.divider()

    col1, col2 = st.columns([1, 3])
    with col1:
        st.download_button("⬇️ Download Results", data=format_export(trigger_results, notifications), file_name="album_results.json", mime="application/json")
    with col2:
        if st.button("🧹 Clear All"):
            clear_all()

elif not uploaded_files:
    st.warning("Please upload at least two images. Album analysis will begin automatically!")

