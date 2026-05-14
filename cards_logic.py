import app.utils
from app import db
import random

def temp_add_cards(): #temporary function to add cards
    i, j = app.utils.get_current_user_id()
    app.utils.add_user_cards(i, [
                ("Flash", 2),
                ("Timestop", 1),
                ("Heal", 1),
                ("Guard", 2),
                ("Parry", 2),
                ("Parry", 2),
                ("Bear Trap", 2),
                ("Dynamite", 2),
                ("Slingshot", 2),
                ("Strip Mine", 2),
                ("Meteor", 2),
                ("Dash Attack", 2),
                ("Key to Victory", 2),
                ("Light the Way", 2),
                ("Master of Movement", 1),
                ("Master of Combat", 1),
                ("Master of Cards", 1),
                ("Master of Survival", 1),
            ])
    '''app.utils.add_user_cards(i, [
                ("Eye for Treasure", 3),
            ])'''
    db.session.commit()

#global deck array
#shuffle 3 cards into hand, remove them from deck array
#Any non chosen cards go back into the deck array, chosen card gets placed in discard slot, decrement used count
def get_deck():
    user_id, err = app.utils.get_current_user_id()
    if err:
        return [], err

    deck, err = app.utils.get_user_deck(user_id)
    if err:
        return [], err

    return [deck_card.user_card for deck_card in deck.deck_cards], None
#cards that are proccessed upon loading the game

class PlayerDeck():
    def __init__(self):
        self.deck = 0
        self.deckMax: int
        self.deckSize: int
        self.deck = []
        self.hand = []
        self.discard = []

    def loadDeck(self):
        for card in self.deck:
            if "Master" in card.card.name:
                print("removed a card")
        self.deck = [card for card in self.deck if "Master" not in card.card.name]
        self.deckMax = len(self.deck)
        self.deckSize = len(self.deck)

    def shuffle(self, cards):
        hand = random.sample(cards, min(3, len(cards)))
        return hand

    def useSlot(self, slot):
        #print(self.hand[slot].card.name)
        card = self.hand[slot]
        self.deck.remove(self.hand[slot])
        self.discard.append(card)
        self.deckSize = len(self.deck)
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