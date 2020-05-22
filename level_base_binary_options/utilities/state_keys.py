from enum import Enum


class StatKeys(Enum):
    BALANCE = "balance"
    NUM_TRADES = 'num_trades'
    WON = 'won'  # daily won count and all won count
    LOSS = 'loss'  # daily won count and all loss count
    DRAW = 'draw'  # daily draw count
    BINARY = 'binary'  # binary trade count
    LEVELS = 'levels'  # level trade count
    BUY = 'buy'  # buy trade count
    SELL = 'sell'  # sell trade count
    D_WON = 'd_won'  # daily won amount and all won amount
    D_LOSS = 'd_loss'  # daily loss amount and all loss amount
    LEVEL_1 = '1'  # level 1 selected times as a count
    LEVEL_2 = '2'  # level 2 selected count as a count
    LEVEL_3 = '3'  # level 3 selected count as a count
    LEVEL_4 = '4'  # level 4 selected count as a count
    LEVEL_1_INVST = '1_invest'  # level 1 total investment
    LEVEL_2_INVST = '2_invest'  # level 2 total investment
    LEVEL_3_INVST = '3_invest'  # level 3 total investment
    LEVEL_4_INVST = '4_invest'  # level 4 total investment
    LEVEL_1_WON_COUNT = '1_won_count'  # level 1 won count
    LEVEL_2_WON_COUNT = '2_won_count'  # level 2 won count
    LEVEL_3_WON_COUNT = '3_won_count'  # level 3 won count
    LEVEL_4_WON_COUNT = '4_won_count'  # level 4 won count
    LEVEL_1_LOSS_COUNT = '1_loss_count'  # level 1 loss count
    LEVEL_2_LOSS_COUNT = '2_loss_count'  # level 2 loss count
    LEVEL_3_LOSS_COUNT = '3_loss_count'  # level 3 loss count
    LEVEL_4_LOSS_COUNT = '4_loss_count'  # level 4 loss count
    LEVEL_1_WON_AMOUNT = '1_won_amount'  # level 1 won amount
    LEVEL_2_WON_AMOUNT = '2_won_amount'  # level 2 won amount
    LEVEL_3_WON_AMOUNT = '3_won_amount'  # level 3 won amount
    LEVEL_4_WON_AMOUNT = '4_won_amount'  # level 4 won amount
    LEVEL_1_LOSS_AMOUNT = '1_loss_amount'  # level 1 loss Amount
    LEVEL_2_LOSS_AMOUNT = '2_loss_amount'  # level 2 loss Amount
    LEVEL_3_LOSS_AMOUNT = '3_loss_amount'  # level 3 loss Amount
    LEVEL_4_LOSS_AMOUNT = '4_loss_amount'  # level 4 loss Amount
