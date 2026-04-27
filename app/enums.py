import enum

class CardRarity(enum.Enum):
    common = "common"
    uncommon = "uncommon"
    rare = "rare"
    legendary = "legendary"
    master = "master"


class CardType(enum.Enum):
    movement = "movement"
    survival = "survival"
    combat = "combat"
    utility = "utility"
    debuff = "debuff"


class TradeStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
