from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import base64
import io
import numpy as np
from PIL import Image
from ml.scripts.pipeline import scan_card
from .models import (db, Card, SavedCard, WishlistItem)
from .report import analyze_card

views = Blueprint("views", __name__)

#Home page
@views.route("/")
def home():
    return render_template("index.html")


#Scan route
@views.route("/scan", methods=["POST"])
def scan():

    #Get base64 image from frontend
    data = request.get_json()
    image_data = data["image"]

    #Remove base64 header
    image_data = image_data.split(",")[1]

    #Decode image
    image_bytes = base64.b64decode(image_data)

    #Convert to PIL image
    image = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    #Convert to numpy array for ML model
    img = np.array(image)

    #Run ML pipeline
    result = scan_card(img)

    #If scan fails
    if not result["success"]:
        return jsonify(result)

    #Normalize card name
    card_name = result["card"].replace("_", " ")

    #Find card in database
    card = Card.query.filter_by(
        name=card_name
    ).first()

    #If card is not found in DB
    if not card:
        return jsonify({
            "success": True,
            "card": result["card"],
            "confidence": result["confidence"]
        })

    #Removing card from wishlist
    if current_user.is_authenticated:

        WishlistItem.query.filter_by(
            user_id=current_user.id,
            card_id=card.id
        ).delete()

        db.session.commit()

    #Returning card data
    return jsonify({

        "success": True,

        "card": card.name,
        "confidence": result["confidence"],

        "image": card.image_url,
        "mana_cost": card.mana_cost,
        "oracle_text": card.oracle_text,
        "rarity": card.rarity,
        "set": card.set_name,
        "price": card.market_price
    })
    
#Getting all cards
@views.route("/api/cards")
def all_cards():

    cards = Card.query.all()

    return jsonify([
        {
            "id": card.id,
            "name": card.name,
            "image": card.image_url,
            "price": card.market_price
        }
        for card in cards
    ])

#Getting the card's detail
@views.route("/api/card/<int:card_id>")
def card_details(card_id):

    card = Card.query.get(card_id)

    if not card:
        return jsonify({"success": False})

    return jsonify({
        "success": True,
        "id": card.id,
        "name": card.name,
        "image": card.image_url,
        "mana_cost": card.mana_cost,
        "oracle_text": card.oracle_text,
        "rarity": card.rarity,
        "set": card.set_name,
        "price": card.market_price
    })

#Saving card to their user
@views.route("/api/save-card", methods=["POST"])
@login_required
def save_card():

    data = request.get_json()

    #Find card by name
    card = Card.query.filter_by(
        name=data["card_name"]
    ).first()

    if not card:
        return jsonify({"success": False})

    #Prevent duplicates
    exists = SavedCard.query.filter_by(
        user_id=current_user.id,
        card_id=card.id
    ).first()

    if exists:
        return jsonify({
            "success": False,
            "message": "Already Saved"
        })

    #Save card
    save = SavedCard(
        user_id=current_user.id,
        card_id=card.id
    )

    db.session.add(save)
    db.session.commit()

    return jsonify({"success": True})

#Wishlist page
@views.route("/wishlist")
@login_required
def wishlist():
    return render_template("wishlist.html")


#Loading cards in wishlist
@views.route("/api/wishlist")
@login_required
def wishlist_cards():

    cards = WishlistItem.query.filter_by(
        user_id=current_user.id
    ).all()

    return jsonify([
        {
            "id": Card.query.get(item.card_id).id,
            "name": Card.query.get(item.card_id).name,
            "image": Card.query.get(item.card_id).image_url,
            "price": Card.query.get(item.card_id).market_price
        }
        for item in cards
    ])

#Collections page
@views.route("/collections")
@login_required
def collections_page():
    return render_template("collections.html")

#Cards page
@views.route("/cards")
def cards_page():
    return render_template("cards.html")


#Saving cards
@views.route("/api/saved-cards")
@login_required
def saved_cards():

    cards = SavedCard.query.filter_by(
        user_id=current_user.id
    ).order_by(
        SavedCard.id.desc()
    ).all()

    return jsonify([
        {
            "id": Card.query.get(save.card_id).id,
            "name": Card.query.get(save.card_id).name
        }
        for save in cards
    ])

#Adding items to wishlist
@views.route("/api/wishlist/add", methods=["POST"])
@login_required
def add_wishlist():

    data = request.get_json()

    #Check if already exists
    exists = WishlistItem.query.filter_by(
        user_id=current_user.id,
        card_id=data["card_id"]
    ).first()

    if exists:
        return jsonify({"success": False})

    item = WishlistItem(
        user_id=current_user.id,
        card_id=data["card_id"]
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({"success": True})

#User's status
@views.route("/api/user")
def get_user():

    return jsonify({
        "logged_in": current_user.is_authenticated,
        "username": current_user.username if current_user.is_authenticated else None
    })

#Redirecting a user to a card they own page
@views.route("/card/<int:card_id>")
def card_page(card_id):

    card = Card.query.get(card_id)

    if not card:
        return "Card not found"

    return render_template(
        "card_detail.html",
        card=card
    )
#Links to buy cards
@views.route("/api/card/<int:card_id>/buy-links")
def buy_links(card_id):

    card = Card.query.get(card_id)

    if not card:
        return jsonify({"error": "not found"})

    name = card.name.replace(" ", "+")

    return jsonify({
        "tcgplayer": f"https://www.tcgplayer.com/search/magic/product?q={name}",
        "cardmarket": f"https://www.cardmarket.com/en/Magic/Products/Search?searchString={name}",
        "market_price": card.market_price
    })

#Report analysis
@views.route("/api/card/<int:card_id>/ai")
def card_ai(card_id):

    card = Card.query.get(card_id)

    if not card:
        return jsonify({"error": "not found"})

    return jsonify(analyze_card(card))

#Tracking the pric history (to try and make a graph)
@views.route("/api/card/<int:card_id>/history")
def card_history(card_id):

    card = Card.query.get(card_id)

    if not card:
        return jsonify([])

    base = card.market_price or 1

    return jsonify({
        "prices": [
            base * 0.9,
            base * 1.1,
            base * 1.0,
            base * 1.3,
            base * 1.2,
            base * 1.4,
            base
        ]
    })