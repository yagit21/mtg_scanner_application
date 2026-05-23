import numpy as np
import onnxruntime as ort
from PIL import Image
import json

#Load class names
with open("ml/models/class_names.json", "r") as f:
    class_names = json.load(f)

#Load ONNX classifier
session = ort.InferenceSession(
    "ml/models/card_classifier.onnx",
    providers=["CPUExecutionProvider"]
)
#Getting the name of the input node of the neural network (so I can pass the image data to the model)
input_name = session.get_inputs()[0].name

#Confidence threshold of 90%
clas_threshold = 0.90

#Takes a raw image and formats it for the ResNet model
def preprocess(image):
    #Converts the numpy array image to a PIL image object
    pil_img = Image.fromarray(image)
    #Resizing the image to 224x224 (standard size for ResNet)
    pil_img = pil_img.resize((224, 224))
    #Converts the PIL image back to numpy array (ensuring it is a float then divided by 255, to normalise pixel values)
    img = np.array(pil_img).astype(np.float32) / 255.0

    #Normalising (standard mean and deviation from ImageNet dataset)
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    #Standardises the image (to ensure model focuses on features rather than colour intensity)
    img = (img - mean) / std
    #Converts dimensions from HWC to CHW
    img = np.transpose(img, (2, 0, 1))
    #Adds a batch dimension (model expects a batch)
    img = np.expand_dims(img, axis=0)
    #Returning the processed image
    return img.astype(np.float32)

#Calculating the softmax activation function for a batch of data using NumPy
#(converting raw model ouputs - logits - into probabilities that sum to 1.0)
#e.g. if the model looks at the photo and has logits for three categories [Augury Owl, Blood Artist, Deception] their corresponding input [2.0, 1.0, 0.1] after exponents [7.39, 2.71, 1.10] (sums to 11.20) after division [0.66, 0.24, 0.10]
#There is a 66% chance of Augury Owl, 24% chance Blood Artist, 10% chance it is Deception
def softmax(x):
    #Using the exponential (e^x) for each element in the input (we minus the maximum value from each element first so that the values of e^x are small - with the largest value being 1)
    exp_x = np.exp(x - np.max(x))
    #Dividing each exponential value by the sum of all exponential values in that row (so that the values are between 0 to 1 and sum to 1)
    return exp_x / exp_x.sum(axis=1, keepdims=True)


def classify_card(image):
    #Proccesses the image so the model can use it
    input_tensor = preprocess(image)
    #Executes the model and gives the processed image to the model's input layer
    outputs = session.run(None, {input_name: input_tensor})
    #Gets the unscaled predictions from the model's first ouput layer
    logits = outputs[0]
    #Converts the raw logits into easy to understand percentages 
    probs = softmax(logits)
    #Finds the index of the highest probability value in the array
    predicted_idx = int(np.argmax(probs))
    #Gets the highest probability value for the model's confidence score
    confidence = float(np.max(probs))
    #Checks if the model's confidence is lower than the limit
    if confidence < clas_threshold:
        return {
            "card": "Unknown", #If the confidence is too low returns no card
            "confidence": confidence
        }
    #If the model is confident enough it returns the name of the card
    return {
        "card": class_names[predicted_idx],
        "confidence": confidence
    }