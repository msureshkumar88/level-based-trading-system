from enum import Enum


class StatKeys(Enum):
    BALANCE = "balance"
    NUM_TRADES = 'num_trades'
    WON = 'won'  # daily won count
    LOSS = 'loss'  # daily won count
    DRAW = 'draw'
    BINARY = 'binary'
    LEVELS = 'levels'
    BUY = 'buy'
    SELL = 'sell'
    D_WON = 'd_won'  # daily won amount
    D_LOSS = 'd_loss'  # daily loss amount
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
