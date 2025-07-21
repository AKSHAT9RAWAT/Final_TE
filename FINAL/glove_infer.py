import torch
import torch.nn as nn
import json
import numpy as np
import os


# Load GloVe Embeddings
def load_glove(glove_path="glove.6B.100d.txt"):
    word2vec = {}
    with open(glove_path, encoding="utf8") as f:
        for line in f:
            values = line.strip().split()
            word = values[0]
            vector = np.array(values[1:], dtype='float32')
            word2vec[word] = vector
    return word2vec

def sentence_to_embedding(sentence, word2vec, dim=100):
    words = sentence.lower().split()
    vectors = [word2vec[word] for word in words if word in word2vec]
    if not vectors:
        return torch.zeros(dim)
    return torch.tensor(np.mean(vectors, axis=0), dtype=torch.float)

def album_to_embedding(captions, word2vec, dim=100):
    caption_embeddings = [sentence_to_embedding(c, word2vec, dim) for c in captions]
    return torch.stack(caption_embeddings).mean(dim=0)

# Model Definition
class GloveTriggerModel(nn.Module):
    def __init__(self, input_dim=100):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(128, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.sigmoid(x)
        return x

# Inference
glove_path = "glove.6B.100d.txt"
# Use environment variables if provided, else default to fixed filenames
input_path = os.environ.get("INPUT_PATH", os.path.join("FINAL", "trigger_input.json"))
output_path = os.environ.get("OUTPUT_PATH", os.path.join("FINAL", "trigger_output.json"))
threshold = 0.4

word2vec = load_glove(glove_path)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "glove_trigger_model_finetuned.pt")
model = GloveTriggerModel()
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cpu")))
model.eval()

with open(input_path, "r") as f:
    album_data = json.load(f)

results = {}

with torch.no_grad():
    for album_id, album in album_data.items():
        captions = album.get("captions", [])
        embedding = album_to_embedding(captions, word2vec)
        prob = model(embedding.unsqueeze(0)).item()
        pred = int(prob >= threshold)

        results[album_id] = {
            "captions": captions,
            "probability": round(prob, 4),
            "label": pred
        }

with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\u2705 Inference complete. Saved to {output_path}")
