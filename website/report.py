import random

def analyze_card(card):

    #Base score starts at 0
    score = 0

    #Prices:
    #High value cards get higher score
    if card.market_price and card.market_price > 10:
        score += 3
    elif card.market_price and card.market_price > 3:
        score += 2
    else:
        score += 1

    #Orcale text rating
    #Strong removal keyword bonus
    if card.oracle_text and "destroy" in card.oracle_text.lower():
        score += 2

    #Card draw = strong utility bonus
    if card.oracle_text and "draw" in card.oracle_text.lower():
        score += 2

    #Bonus if it is rare
    if card.rarity == "mythic":
        score += 2


    #Final rating system
    if score >= 6:
        rating = "🔥 Meta Staple"
    elif score >= 4:
        rating = "⭐ Strong Card"
    elif score >= 2:
        rating = "👍 Playable"
    else:
        rating = "🟡 Casual"

    #Returning analysis result
    return {
        "rating": rating,
        "score": score,
        "comment": random.choice([
            "Strong card for its cost.",
            "Works well in many decks.",
            "Situational but useful.",
            "High synergy potential."
        ])
    }