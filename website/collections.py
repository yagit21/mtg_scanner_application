from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from .models import (db, Collection, CollectionCard, Card, WishlistItem)

collections = Blueprint("collections", __name__)

#All collections
@collections.route("/api/collections")
@login_required
def get_collections():

    #Get all collections for current user
    items = Collection.query.filter_by(
        user_id=current_user.id
    ).all()

    return jsonify([
        {
            "id": c.id,
            "name": c.name
        }
        for c in items
    ])

#Get collection
@collections.route("/api/collections/<int:id>")
@login_required
def collection_details(id):

    #Find collection belonging to user
    collection = Collection.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first()

    if not collection:
        return jsonify([])

    #Get cards inside collection
    cards = CollectionCard.query.filter_by(
        collection_id=collection.id
    ).all()

    output = []

    for item in cards:

        card = Card.query.get(item.card_id)

        if not card:
            continue

        output.append({
            "id": card.id,
            "name": card.name,
            "image": card.image_url,
            "rarity": card.rarity,
            "price": card.market_price,
            "quantity": item.quantity
        })

    return jsonify(output)

#Create collection
@collections.route("/api/collections/create", methods=["POST"])
@login_required
def create_collection():

    data = request.get_json()

    name = (data.get("name") or "").strip()
    cards = data.get("cards", [])

    #Validate name
    if not name:
        return jsonify({
            "success": False,
            "message": "Collection name required"
        })

    #Create collection
    collection = Collection(
        name=name,
        user_id=current_user.id
    )

    db.session.add(collection)
    db.session.commit()

    #Add cards safely (remove duplicates)
    for card_id in set(cards):

        if not isinstance(card_id, int):
            continue

        db.session.add(CollectionCard(
            collection_id=collection.id,
            card_id=card_id,
            quantity=1
        ))

        #Remove from wishlist if exists
        WishlistItem.query.filter_by(
            user_id=current_user.id,
            card_id=card_id
        ).delete()

    db.session.commit()

    return jsonify({
        "success": True,
        "collection_id": collection.id
    })

#Add card to collection
@collections.route("/api/collections/add-card", methods=["POST"])
@login_required
def add_card():

    data = request.get_json()

    collection_id = data.get("collection_id")
    card_id = data.get("card_id")

    #Verify the user's ownership
    collection = Collection.query.filter_by(
        id=collection_id,
        user_id=current_user.id
    ).first()

    if not collection:
        return jsonify({
            "success": False,
            "message": "Invalid collection"
        })

    #Check if card already exists
    existing = CollectionCard.query.filter_by(
        collection_id=collection_id,
        card_id=card_id
    ).first()

    if existing:
        existing.quantity += 1
    else:
        db.session.add(CollectionCard(
            collection_id=collection_id,
            card_id=card_id,
            quantity=1
        ))

    db.session.commit()

    return jsonify({"success": True})

#Removing card from collection
@collections.route("/api/collections/remove-card", methods=["POST"])
@login_required
def remove_card():

    data = request.get_json()

    #Find card inside collection for user
    card = CollectionCard.query.join(Collection).filter(
        CollectionCard.collection_id == data["collection_id"],
        CollectionCard.card_id == data["card_id"],
        Collection.user_id == current_user.id
    ).first()

    if card:
        db.session.delete(card)
        db.session.commit()

    return jsonify({"success": True})

#Deleting collections
@collections.route("/api/collections/delete/<int:id>", methods=["DELETE"])
@login_required
def delete_collection(id):

    collection = Collection.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first()

    if not collection:
        return jsonify({"success": False})

    #Delete child cards first
    CollectionCard.query.filter_by(
        collection_id=collection.id
    ).delete()

    db.session.delete(collection)
    db.session.commit()

    return jsonify({"success": True})