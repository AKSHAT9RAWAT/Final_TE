import json
from pathlib import Path
from collections import Counter
import sys
import os

# Event tag keywords
EVENT_TAGS = {
    "birthday": ["birthday", "cake", "candles", "present", "gift", "balloons"],
    "wedding": ["wedding", "bride", "groom", "aisle", "altar", "reception", "vows"],
    "graduation": ["graduation", "gown", "diploma", "cap", "ceremony", "degree"],
    "sports": ["trophy", "race", "match", "team", "goal", "sports", "field"],
    "picnic": ["picnic", "blanket", "basket", "grass", "tree", "sandwich"],
    "festival": ["parade", "festival", "float", "costume", "lantern", "celebration"],
    "travel": ["beach", "mountain", "sunset", "trip", "boat", "vacation"],
    "pets": ["dog", "puppy", "cat", "kitten", "pet", "pets", "leash", "animal", "fur", "bark", "meow", "playing fetch"],
    "parade": ["parade", "march", "balloons", "flags", "crowd", "banner", "music", "drum", "cheer"],
    "swimming": ["swimming", "pool", "swim", "float", "goggles", "diving", "splash", "swimsuit"],
    "seminar_event": ["presentation", "conference", "projector", "screen", "auditorium", "audience", "speaker", "microphone", "stage", "session", "event", "nasa"]
}

# Template captions and notifications (no emojis)
TEMPLATES = {
    "birthday": "Someone’s birthday bash! Want to create a memory?",
    "wedding": "A beautiful wedding captured! Shall we build your story?",
    "graduation": "Graduation day vibes! Ready to celebrate your journey?",
    "sports": "Game time moments! Let’s craft your winning memory!",
    "picnic": "Picnic memories in the open! Want to share it?",
    "festival": "Celebrating traditions! Let's make this story special!",
    "travel": "Travel diaries look exciting! Want to save the journey?",
    "pets": "Furry friends captured! Want to relive your pet moments?",
    "parade": "A colorful parade in action! Ready to capture the joy?",
    "swimming": "Making a splash! Shall we dive into this memory?",
    "seminar_event": "Professional moments spotted! Shall we turn this session into a story?"
}

# Generic fallbacks
GENERIC_CAPTIONS = [
    "A special day filled with unforgettable memories.",
    "Moments that matter, captured forever.",
    "Smiles, stories, and a sprinkle of magic.",
    "A beautiful memory in the making.",
    "Celebrating life one photo at a time."
]

GENERIC_NOTIFICATIONS = [
    "Looks like you've captured something memorable! Want to create a story?",
    "A meaningful memory spotted! Ready to turn it into a post?",
    "Looks important! Want to build a moment around it?"
]

def extract_tags(caption):
    tags = []
    text = caption.lower()
    for tag, keywords in EVENT_TAGS.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)
    return tags

def generate_caption_and_prompt(album_id, tag_counts):
    if tag_counts:
        top_tag = tag_counts.most_common(1)[0][0]
        caption = TEMPLATES.get(top_tag, GENERIC_CAPTIONS[0])
        prompt = TEMPLATES.get(top_tag, GENERIC_NOTIFICATIONS[0])
    else:
        caption = GENERIC_CAPTIONS[hash(album_id) % len(GENERIC_CAPTIONS)]
        prompt = GENERIC_NOTIFICATIONS[hash(album_id) % len(GENERIC_NOTIFICATIONS)]
    return caption, prompt

def process_albums(input_json, output_json):
    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    output = {}

    for album_id, item in data.items():
        if item.get("label") != 1:
            continue  # Skip non-meaningful albums

        captions = item.get("captions", [])
        tag_counter = Counter()

        for cap in captions:
            tag_counter.update(extract_tags(cap))

        generated_caption, notification = generate_caption_and_prompt(album_id, tag_counter)

        output[album_id] = {
            "captions": captions,
            "tags": list(tag_counter.keys()),
            "generated_caption": generated_caption,
            "notification_prompt": notification
        }

    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    print(f"\u2705 Done! Output saved to: {output_json}")

# Example usage
if __name__ == "__main__":
    input_json = sys.argv[1] if len(sys.argv) > 1 else os.path.join("FINAL", "trigger_output.json")
    output_json = sys.argv[2] if len(sys.argv) > 2 else os.path.join("FINAL", "notification_output.json")
    process_albums(input_json, output_json)
