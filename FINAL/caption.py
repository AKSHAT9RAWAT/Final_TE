from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import os
import json
from collections import defaultdict

# Load BLIP model and processor from local directory
BLIP_LOCAL_PATH= "blip_model/models--Salesforce--blip-image-captioning-base/snapshots/82a37760796d32b1411fe092ab5d4e227313294b"
processor = BlipProcessor.from_pretrained(BLIP_LOCAL_PATH)
model = BlipForConditionalGeneration.from_pretrained(BLIP_LOCAL_PATH)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

def extract_caption(image_path):
    image = Image.open(image_path).convert('RGB')
    inputs = processor(images=image, return_tensors="pt").to(device)
    out = model.generate(**inputs, max_new_tokens=50)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption

def extract_image_and_cluster_captions(album_dirs, base_folder):
    image_extensions = [".jpg", ".jpeg", ".png", ".bmp"]
    image_captions = {}
    cluster_captions = defaultdict(list)

    for album in album_dirs:
        album_path = os.path.join(base_folder, album)
        if not os.path.isdir(album_path):
            continue

        for filename in sorted(os.listdir(album_path)):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                image_path = os.path.join(album_path, filename)
                print(f"📸 Captioning {album}/{filename}...")
                try:
                    caption = extract_caption(image_path)
                    image_key = f"{album}/{filename}"
                    image_captions[image_key] = caption
                    cluster_captions[album].append(caption)
                except Exception as e:
                    print(f"❌ Error with {album}/{filename}: {e}")

    return image_captions, cluster_captions

def get_album_batches(base_folder, batch_size=50):
    all_albums = [d for d in sorted(os.listdir(base_folder)) if os.path.isdir(os.path.join(base_folder, d))]
    batches = [all_albums[i:i + batch_size] for i in range(0, len(all_albums), batch_size)]
    return batches

def convert_cluster_to_trigger_input(cluster_json, trigger_input_json):
    print_step("Converting cluster captions to trigger input format...")
    import json
    with open(cluster_json, "r") as f:
        clusters = json.load(f)
    trigger_input = {album: {"captions": captions} for album, captions in clusters.items()}
    with open(trigger_input_json, "w") as f:
        json.dump(trigger_input, f, indent=2)

if __name__ == "__main__":
    base_folder = os.environ.get("BASE_FOLDER", "personal_test")
    output_folder = os.environ.get("OUTPUT_FOLDER", "personal_capt")
    batch_size = int(os.environ.get("BATCH_SIZE", "50"))

    os.makedirs(output_folder, exist_ok=True)
    batches = get_album_batches(base_folder, batch_size=batch_size)
    print(f"📦 Total batches to process: {len(batches)}")

    for batch_num, album_batch in enumerate(batches, start=1):
        print(f"\n🚀 Starting batch {batch_num} with {len(album_batch)} albums...")

        image_caps, cluster_caps = extract_image_and_cluster_captions(album_batch, base_folder)

        with open(os.path.join(output_folder, f"image_captions_batch_{batch_num}.json"), "w") as f:
            json.dump(image_caps, f, indent=2)

        with open(os.path.join(output_folder, f"cluster_captions_batch_{batch_num}.json"), "w") as f:
            json.dump(cluster_caps, f, indent=2)

        print(f"✅ Batch {batch_num} completed and saved.")

    print("\n🎉 All batches processed successfully.")
