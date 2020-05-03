from enum import Enum


class StatKeys(Enum):
    BALANCE = "balance"
    NUM_TRADES = 'num_trades'
    WON = 'won'  # daily won count
    LOSS = 'loss'  # daily won count
    DRAW = 'draw'   # daily draw count
    BINARY = 'binary'  # binary trade count
    LEVELS = 'levels'  # level trade count
    BUY = 'buy'  # buy trade count
    SELL = 'sell'  # sell trade count
    D_WON = 'd_won'  # daily won amount
    D_LOSS = 'd_loss'  # daily loss amount
    LEVEL_1 = '1'  # level 1 selected count
    LEVEL_2 = '2'  # level 2 selected count
    LEVEL_3 = '3'  # level 3 selected count
    LEVEL_4 = '4'  # level 4 selected count
