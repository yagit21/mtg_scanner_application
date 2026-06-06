from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )


class Card(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    image_url = db.Column(
        db.String(500)
    )

    mana_cost = db.Column(
        db.String(100)
    )

    oracle_text = db.Column(
        db.Text
    )

    rarity = db.Column(
        db.String(50)
    )

    set_name = db.Column(
        db.String(100)
    )

    market_price = db.Column(
        db.Float,
        default=0
    )


class SavedCard(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    card_id = db.Column(
        db.Integer,
        db.ForeignKey("card.id"),
        nullable=False
    )


class WishlistItem(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    card_id = db.Column(
        db.Integer,
        db.ForeignKey("card.id"),
        nullable=False
    )


class Collection(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    # 🔥 IMPORTANT: auto-delete all cards when collection is deleted
    cards = relationship(
        "CollectionCard",
        backref="collection",
        cascade="all, delete-orphan"
    )


class CollectionCard(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    collection_id = db.Column(
        db.Integer,
        db.ForeignKey("collection.id"),
        nullable=False
    )

    card_id = db.Column(
        db.Integer,
        db.ForeignKey("card.id"),
        nullable=False
    )

    quantity = db.Column(db.Integer, default=1)

    # 🔥 PREVENT DUPLICATES PER COLLECTION
    __table_args__ = (
        db.UniqueConstraint(
            "collection_id",
            "card_id",
            name="unique_card_per_collection"
        ),
    )