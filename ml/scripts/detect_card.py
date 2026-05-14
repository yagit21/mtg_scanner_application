from ultralytics import YOLO
import cv2

#Loading the model (to be used to detect the cards)
model = YOLO("ml/models/best.pt")

#Minimum confidence required to detect a card (60%)
detection_threshold = 0.6

#Finding where the card is using best model and then return the card 
def detect_card(image):
    #Pass the image into YOLO model (returns predictions [bounding boxes and confidence scores])
    results = model(image)
    #Get the first image from the result
    result = results[0]
    #If there is no objects detected
    if len(result.boxes) == 0:
        return None

    #Best detection (best bounding box and highest confidence score)
    best_box = None
    best_conf = 0
    #Looping through each detection (if YOLO detects more than one object)
    for box in result.boxes:
        #Getting the confidence score
        conf = float(box.conf[0])
        #Replacing previous best if another better one is found
        if conf > best_conf:
            best_conf = conf
            best_box = box
    #If the best detection is lower than 60% then return nothing
    if best_conf < detection_threshold:
        return None
    #Getting the bounding box coordinates
    x1, y1, x2, y2 = best_box.xyxy[0]
    #Converting them into integers
    x1 = int(x1)
    y1 = int(y1)
    x2 = int(x2)
    y2 = int(y2)
    #Slicing the image array to extract only the detected object region (card)
    crop = image[y1:y2, x1:x2]
    #Returning cropped card image
    return crop
