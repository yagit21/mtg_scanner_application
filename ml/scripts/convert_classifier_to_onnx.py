import torch
import torch.nn as nn
from torchvision import models
import json

#Load class names
with open("ml/models/class_names.json", "r") as f:
    class_names = json.load(f)

num_classes = len(class_names)

#Recreate the same architecture
model = models.resnet18(weights=None)

#Recreate the same final layer
model.fc = nn.Linear(model.fc.in_features, num_classes)

#Load trained weights
model.load_state_dict(
    torch.load(
        "ml/models/card_classifier.pth",
        map_location="cpu"
    )
)

model.eval()

#Dummy input
dummy_input = torch.randn(1, 3, 224, 224)

#Export to ONNX
torch.onnx.export(
    model,
    dummy_input,
    "ml/models/card_classifier.onnx",
    input_names=["input"],
    output_names=["output"],
    opset_version=11
)

print("Classifier converted to ONNX.")