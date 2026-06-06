from ml.scripts.detect_card import detect_card
from ml.scripts.classify_card import classify_card


def scan_card(frame):

    crop = detect_card(frame) #Detecting there is a card using the YOLO model
    #If it returns no crop region of the card
    if crop is None:
        return {"success": False, "message": "No card detected"} #There is no card in the image
    #If it returns a crop region of the card (gets the prediction of the card using the ResNet model)
    prediction = classify_card(crop)
    
    return {
        "success": True,
        "card": prediction["card"],
        "confidence": round(
            prediction["confidence"],
            2
        )
    }