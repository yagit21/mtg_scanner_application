import cv2
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import numpy as np
import json

#Classnames
with open("ml/models/class_names.json", "r") as f:
    class_names = json.load(f)

num_classes = len(class_names)


model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=True)
model.fc = nn.Linear(model.fc.in_features, num_classes)
model.load_state_dict(torch.load("ml/models/card_classifier.pth", map_location="cpu"))
model.eval()


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


clas_threshold = 0.75


def classify_card(image):

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    pil_img = Image.fromarray(rgb)

    tensor = transform(pil_img).unsqueeze(0)

    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probs, 1)

    confidence = float(confidence.item())

    predicted_idx = int(predicted.item())

    #If the confidence is below 75%
    if confidence < clas_threshold:
        return {"card": "Unknown", "confidence": confidence}

    return {"card": class_names[predicted_idx], "confidence": confidence}
