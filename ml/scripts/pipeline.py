from ml.scripts.detect_card import detect_card
from ml.scripts.classify_card import classify_card


def scan_card(frame):

    crop = detect_card(frame)

    if crop is None:
        return { "success": False, "message": "No card detected"}

    prediction = classify_card(crop)

    return {
        "success": True,
        "card": prediction["card"],
        "confidence": round(prediction["confidence"], 2)
    }