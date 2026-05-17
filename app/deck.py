import app.utils
from app import db
import random
from app.models import UserCard

def get_deck():
    user_id, err = app.utils.get_current_user_id()
    if err:
        return [], err

    deck, err = app.utils.get_user_deck(user_id)
    if err:
        return [], err

    return [deck_card.user_card for deck_card in deck.deck_cards], None

class PlayerDeck():
    def __init__(self):
        self.deck = 0
        self.deckMax: int
        self.deckSize: int
        self.deck = []
        self.hand = []
        self.discard = []
        self.master_cards = []
        self.combat_bonus = 0.0
        self.combat_counter = 0
        self.movement_counter = 0
        self.utility_counter = 0
        self.survival_counter = 0

    def loadDeck(self):
        '''Loads user's deck into the game'''
        for card in self.deck:
            if "Master" in card.card.name: #master cards are automatically activated
                self.master_cards.append(card.card.name)
        self.deck = [card for card in self.deck if "Master" not in card.card.name] #exclude master cards 
        self.deckMax = len(self.deck)
        self.deckSize = len(self.deck)

    def shuffle(self, cards):
        if len(cards) <= 3:
            hand = list(cards)
            return hand

        remaining = list(cards)
        hand = []
        for _ in range(min(3, len(remaining))):
            weights = [
                1 + self.combat_bonus if card.card.type == app.enums.CardType.combat else 1
                for card in remaining
            ]
            choice = random.choices(remaining, weights=weights, k=1)[0]
            hand.append(choice)
            remaining.remove(choice)
        return hand

    def useSlot(self, slot):
        card = self.hand[slot]

        self.deck.remove(card)
        self.discard.append(card)
        self.deckSize = len(self.deck)

        db_card = db.session.merge(card)

        if db_card.uses_remaining != -1:
            db_card.uses_remaining -= 1
            card.uses_remaining = db_card.uses_remaining

            if db_card.uses_remaining == 0:
                db.session.delete(db_card)

        db.session.commit()
        return card
        
    def serialize_card(self, user_card):
            if user_card:
                return {
                    "id": user_card.id,
                    "name": user_card.card.name,
                    "effect": user_card.card.effect,
                    "type": user_card.card.type.value,
                    "rarity": user_card.card.rarity.value,
                    "uses_remaining": user_card.uses_remaining,
                    "uses": user_card.card.uses,
                    "max_in_deck": user_card.card.max_in_deck,
                }