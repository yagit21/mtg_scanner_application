import cv2
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import numpy as np
import json

#Class names that the model can identify 
with open("ml/models/class_names.json", "r") as f:
    class_names = json.load(f)

num_classes = len(class_names)

#Downloading the pretained resnet model to recongise the type of card to the class name
model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=True)
model.fc = nn.Linear(model.fc.in_features, num_classes) #Replacing the final layer of the model to match the number of classes 
model.load_state_dict(torch.load("ml/models/card_classifier.pth", map_location="cpu"))
model.eval() #Preparing the model for predictions

#In order for model to recognise the image, the image must be prepared in the same way the it was given to the model trained
transform = transforms.Compose([
    transforms.Resize((224, 224)), #Resize the image to 224 by 224 pixels
    transforms.ToTensor(), #Converts the pixel to an tensor format
    transforms.Normalize( #Normalising image colour (helps the model focus on features of the card rather than brightness/contrast variations)
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])
#The classification threshold has to be a minimum of 90% for it to detect the card
clas_threshold = 0.90

def classify_card(image):
    #Convert the image from OpenCV (BGR) to an RGB
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #Convert the RGB to a pillow image
    pil_img = Image.fromarray(rgb)
    #Applies the transformations to the image and converting the sample to a batch so it can be processed by the model 
    tensor = transform(pil_img).unsqueeze(0)
    #Runs the image through the model with torch.no_grad() (to save memory by disballing gradient calculations)
    with torch.no_grad():
        outputs = model(tensor) #Passing the data to the model to generate the predictions
        probs = torch.softmax(outputs, dim=1) #Calculating the probability using torch.softmax (converting the raw output scores to class probabilities)
        confidence, predicted = torch.max(probs, 1) #Confidence stores the max probability found, predicted stores the index of the highest value

    confidence = float(confidence.item()) #Getting the confidence number 

    predicted_idx = int(predicted.item()) #Getting the index of the highest confidence

    #If the confidence is below 90%
    if confidence < clas_threshold:
        return {"card": "Unknown", "confidence": confidence} #The card is not know

    return {"card": class_names[predicted_idx], "confidence": confidence} #Returning the card using the index and the confidence rating
