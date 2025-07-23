import torch
from glove_train import GloveTriggerModel

model = GloveTriggerModel(input_dim=100)
model.load_state_dict(torch.load('FINAL/glove_trigger_model_finetuned.pt', map_location='cpu'))
model.eval()

dummy_input = torch.randn(1, 100)

torch.onnx.export(
    model,
    dummy_input,
    "glove_trigger_model.onnx",
    input_names=['input'],
    output_names=['output'],
    opset_version=11
)

print("Exported to glove_trigger_model.onnx") 