import os
import sys
import shutil
import subprocess
import json

FINAL_DIR = os.path.abspath("FINAL")
VIST_VAL_DIR = os.path.abspath("VIST_VAL")
NUM_ALBUMS = 5

# Utility to print step headers
def print_step(msg):
    print(f"\n{'='*40}\n{msg}\n{'='*40}")

def get_first_n_albums(src_dir, n):
    albums = [d for d in sorted(os.listdir(src_dir)) if os.path.isdir(os.path.join(src_dir, d))]
    return albums[:n]

def prepare_temp_input(albums):
    temp_input = os.path.join(FINAL_DIR, "temp_input")
    if os.path.exists(temp_input):
        shutil.rmtree(temp_input)
    os.makedirs(temp_input, exist_ok=True)
    for album in albums:
        shutil.copytree(os.path.join(VIST_VAL_DIR, album), os.path.join(temp_input, album))
    return temp_input

def run_captioning(temp_input, batch_size=5):
    print_step("Step 1: Generating captions for images using BLIP...")
    env = os.environ.copy()
    env["BASE_FOLDER"] = temp_input
    env["OUTPUT_FOLDER"] = FINAL_DIR
    env["BATCH_SIZE"] = str(batch_size)
    subprocess.run([sys.executable, os.path.join(FINAL_DIR, "caption.py")], env=env, check=True)

def convert_cluster_to_trigger_input(cluster_json, trigger_input_json):
    print_step("Converting cluster captions to trigger input format...")
    with open(cluster_json, "r") as f:
        clusters = json.load(f)
    trigger_input = {album: {"captions": captions} for album, captions in clusters.items()}
    with open(trigger_input_json, "w") as f:
        json.dump(trigger_input, f, indent=2)

def run_trigger_model(trigger_input_json, trigger_output_json):
    print_step("Step 2: Running GloVe trigger model for album classification...")
    env = os.environ.copy()
    env["INPUT_PATH"] = trigger_input_json
    env["OUTPUT_PATH"] = trigger_output_json
    subprocess.run([sys.executable, os.path.join(FINAL_DIR, "glove_infer.py")], env=env, check=True)

def run_notification(trigger_output_json, notification_output_json):
    print_step("Step 3: Generating notifications for label 1 albums...")
    subprocess.run([
        sys.executable, os.path.join(FINAL_DIR, "notification.py"),
        trigger_output_json, notification_output_json
    ], check=True)

def main():
    os.makedirs(FINAL_DIR, exist_ok=True)
    # 1. Get first 5 albums
    print_step("Selecting first 5 albums from VIST_VAL...")
    albums = get_first_n_albums(VIST_VAL_DIR, NUM_ALBUMS)
    print(f"Selected albums: {albums}")
    # 2. Prepare temp input
    temp_input = prepare_temp_input(albums)
    # 3. Run captioning
    run_captioning(temp_input, batch_size=NUM_ALBUMS)
    # Convert cluster_captions_batch_1.json to trigger_input.json
    cluster_json = os.path.join(FINAL_DIR, "cluster_captions_batch_1.json")
    trigger_input_json = os.path.join(FINAL_DIR, "trigger_input.json")
    convert_cluster_to_trigger_input(cluster_json, trigger_input_json)
    # 4. Run trigger model (use trigger_input.json as input)
    trigger_output_json = os.path.join(FINAL_DIR, "trigger_output.json")
    run_trigger_model(trigger_input_json, trigger_output_json)
    # 5. Run notification
    notification_output_json = os.path.join(FINAL_DIR, "notification_output.json")
    run_notification(trigger_output_json, notification_output_json)
    # 6. Cleanup temp input
    shutil.rmtree(temp_input)
    print_step("Pipeline complete! All outputs are in the FINAL folder.")
    print(f"\n- Trigger input: {trigger_input_json}\n- Trigger output: {trigger_output_json}\n- Notifications: {notification_output_json}\n")

if __name__ == "__main__":
    main() 