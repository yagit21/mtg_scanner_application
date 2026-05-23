from PIL import Image
import numpy as np
import onnxruntime as ort


#Loading ONNX YOLO model
session = ort.InferenceSession("ml/models/best.onnx", providers=["CPUExecutionProvider"])
#Getting the name of the input node of the neural network (so I can pass the image data to the model)
input_name = session.get_inputs()[0].name

#Minimum confidence required to detect a card (60%)
detection_threshold = 0.6

def preprocess(image):
    #Converting numpy array to PIL image
    img = Image.fromarray(image)
    #Changing the image size to 640 by 640
    img = img.resize((640, 640))
    #Converting back to NumPy array
    img = np.array(img)
    #Normalising the pixel values to become decimals (helps the data process more efficiently)
    img = img.astype(np.float32) / 255.0
    #Changes the data format to Channel-Height-Width which is what the framework requires
    img = np.transpose(img, (2, 0, 1))
    #Adds an extra dimension to the batch size (even if we are only processing one image the model excepts a shape)
    img = np.expand_dims(img, axis=0)

    return img  

#Finding where the card is using best model and then return the card 
def detect_card(image):
    #Getting the original height and width of the input image
    original_h, original_w = image.shape[:2]
    #Converting the image into the format the model requires
    input_tensor = preprocess(image)
    #Putting the image into the ONNX model to get predictions
    outputs = session.run(None, {input_name: input_tensor})
    #Extracting the raw detection data (bounding box, coordinates, confidence scores)
    predictions = outputs[0][0]
    #Since the model might find multiple things we need to find the prediction with the highest confidence score
    best_conf = 0 #Intialising the confidence variable
    best_box = None #As well as the corresponding box location
    #Looping through each detection
    for pred in predictions:
        #The confidence score is the 4th index
        confidence = pred[4]
        #If the current detection is better than the previous best it updates
        if confidence > best_conf:
            #Converts the model output back to pixel coordinates (that map to the original image size)
            x_center, y_center, width, height = pred[:4]
            x1 = int((x_center - width / 2) * original_w / 640)
            y1 = int((y_center - height / 2) * original_h / 640)
            x2 = int((x_center + width / 2) * original_w / 640)
            y2 = int((y_center + height / 2) * original_h / 640)

            best_conf = confidence
            best_box = (x1, y1, x2, y2)
    #If the best found card has a confidence score lower than the limit defined it returns no card
    if best_conf < detection_threshold or best_box is None:
        return None
    #The box coordinates
    x1, y1, x2, y2 = best_box
    #Using NumPy slicing to crop the card out of the original image
    crop = image[y1:y2, x1:x2]
    #Returning the cropped card
    return crop