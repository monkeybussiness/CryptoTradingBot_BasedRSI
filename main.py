import requests.exceptions
from binance import Client
import time
import pandas as pd
import indicators
from datetime import datetime
from binance.enums import HistoricalKlinesType
import urllib3

API_KEY = "TOKEN_API"
SECRET_KEY = "SECRET_KEY"
CAPS = ['Time', 'Open-', 'DATE', 'PERIOD', 'PRICE', 'Volume-', 'TIME', 'Quote asset volume-',
        'Number of trades-', 'Taker buy base asset volume-', 'Taker buy quote asset volume-', 'Ignore-']
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
client = Client(API_KEY, SECRET_KEY, {"verify": False, "timeout": 20})
profit = [0]
future_balance = client.futures_account_balance()
SYMBOL_INPUT = "COIN_SYMBOL"


def check_price():
    a = client.get_symbol_ticker(symbol=f"{SYMBOL_INPUT}")
    a = a["price"]
    return float(a)


def check_balance(asset):
    for balance in future_balance:
        if balance["asset"] == f"{asset}":
            balance = balance["balance"]
            return balance


QUANTITY_SIZE = 'QUANTITY_OF_TRADE'


class Account:
    def __init__(self, trade_statement_buy, trade_statement_sell, trade_statement_buy_stoploss,
                 trade_statement_sell_stoploss, open_trade_size, quantity_size, unrealized_profit):
        self.unrealized_profit = unrealized_profit
        self.quantity_size = quantity_size
        self.trade_statement_buy = trade_statement_buy
        self.trade_statement_sell = trade_statement_sell
        self.trade_statement_buy_stoploss = trade_statement_buy_stoploss
        self.trade_statement_sell_stoploss = trade_statement_sell_stoploss
        self.open_trade_price = open_trade_size


def adjust_leverage(symbol):
    client.futures_change_leverage(symbol=symbol, leverage=MARGIN_LEVEL)


def buy():
    ac.quantity_size = QUANTITY_SIZE
    adjust_leverage(f'{SYMBOL_INPUT}')
    ac.trade_statement_buy = True
    ac.trade_statement_sell = False
    ac.trade_statement_sell_stoploss = False
    ac.trade_statement_buy_stoploss = False
    ac.open_trade_price = check_price()
    ac.unrealized_profit = 0
    client.futures_create_order(symbol=SYMBOL_INPUT, side='BUY', type='MARKET', quantity=QUANTITY_SIZE)


def sell():
    ac.quantity_size = QUANTITY_SIZE
    adjust_leverage(f'{SYMBOL_INPUT}')
    ac.trade_statement_sell = True
    ac.trade_statement_buy = False
    ac.unrealized_profit = 0
    ac.open_trade_price = check_price()
    client.futures_create_order(symbol=SYMBOL_INPUT, side='SELL', type='MARKET', quantity=QUANTITY_SIZE)


def close_buy_trade():
    adjust_leverage(f'{SYMBOL_INPUT}')
    ac.trade_statement_buy = False
    ac.trade_statement_sell = False
    unrealized_profit = (getopenpositions_futures()[['unrealizedProfit'][0]])
    unrealized_profit = unrealized_profit.values.tolist()[0]
    ac.unrealized_profit = unrealized_profit
    profit_money = float(profit[0]) + float(unrealized_profit)
    profit[0] = float(profit[0]) + float(profit_money)
    client.futures_create_order(symbol=SYMBOL_INPUT, side='SELL', type='MARKET', quantity=ac.quantity_size)


def close_sell_trade():
    adjust_leverage(f'{SYMBOL_INPUT}')
    ac.trade_statement_buy = False
    ac.trade_statement_sell = False
    ac.trade_statement_sell_stoploss = False
    ac.trade_statement_buy_stoploss = False
    unrealized_profit = (getopenpositions_futures()[['unrealizedProfit'][0]])
    unrealized_profit = unrealized_profit.values.tolist()[0]
    ac.unrealized_profit = unrealized_profit
    profit_money = float(profit[0]) + float(unrealized_profit)
    profit[0] = float(profit[0]) + float(profit_money)
    client.futures_create_order(symbol=SYMBOL_INPUT, side='BUY', type='MARKET', quantity=ac.quantity_size)


ac = Account(trade_statement_buy=False, trade_statement_sell=False, trade_statement_buy_stoploss=False,
             trade_statement_sell_stoploss=False, open_trade_size=0, quantity_size=0, unrealized_profit=0)

acc_balance = client.futures_account_balance()


def getopenpositions_futures():
    positions = client.futures_account()['positions']
    positions = pd.DataFrame.from_dict(positions)
    positions = positions.loc[positions['symbol'] == f'{SYMBOL_INPUT}']
    return positions


def close_position(trade_statement_buy, trade_statement_sell):
    unrealized_profit = (getopenpositions_futures()[['unrealizedProfit'][0]])
    unrealized_profit = unrealized_profit.values.tolist()[0]
    ac.unrealized_profit = unrealized_profit
    stop_loss = ac.open_trade_price * QUANTITY_SIZE * STOP_LOSS_PERCENT

    print(
        f"stop_loss: {stop_loss} ,quantity_size: {ac.quantity_size}, unrealized_profit = {ac.unrealized_profit}, profit: {profit[0]}")
    if float(unrealized_profit) <= -stop_loss:
        if trade_statement_buy is True:
            close_buy_trade()
            profit_money = float(profit[0]) + float(unrealized_profit)
            profit[0] = float(profit[0]) + float(profit_money)

            ac.trade_statement_buy_stoploss = True
            print(
                f'ВРЕМЯ: {df["TIME"].iat[-1]} | ЦЕНА: {df["PRICE"].iat[-1]}| RSI: {df["RSI"].iat[-1]}|'
                f' BALANCE: {check_balance("USDT")} - ЗАКРЫТА СДЕЛКА ПО СТОПЛОССУ - НОВЫЕ НЕ ОТКРЫВАЮ ПОКА RSI НЕ '
                f'ПОДНИМЕТСЯ ')
        elif trade_statement_sell is True:
            close_sell_trade()
            profit_money = float(profit[0]) + float(unrealized_profit)
            profit[0] = float(profit[0]) + float(profit_money)
            ac.trade_statement_sell_stoploss = True
            print(
                f'ВРЕМЯ: {df["TIME"].iat[-1]} | ЦЕНА: {df["PRICE"].iat[-1]}| RSI: {df["RSI"].iat[-1]}|'
                f' BALANCE: {check_balance("USDT")} - ЗАКРЫТА СДЕЛКА ПО СТОПЛОССУ - НОВЫЕ НЕ ОТКРЫВАЮ ПОКА RSI НЕ '
                f'УПАДЕТ ')
    else:
        pass


MARGIN_LEVEL = "MARGIN LEVEL"
STOP_LOSS_PERCENT = "STOP_LOSS_PERCENT"

while True:

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    price = []
    periods = []
    time_list = []
    date_time = []
    timestamp = client._get_earliest_valid_timestamp(f'{SYMBOL_INPUT}', '1m')
    bars = client.get_historical_klines(SYMBOL_INPUT, '1m', '1 day ago UTC',
                                        klines_type=HistoricalKlinesType.FUTURES)
    for i in range(len(bars)):
        price.append(bars[i][4])
        periods.append(i + 1)
        time_list.append(bars[i][6])

    for i in range(len(time_list)):
        temp = time_list[i]
        temp = str(temp)
        temp = int(temp[:10])
        k = datetime.fromtimestamp(temp)
        date_time.append(k)

    arr = {'PERIODS': periods, "PRICE": price}

    df = pd.DataFrame(arr)
    df['RSI'] = indicators.rsi(df, 8, True)
    df[CAPS[6]] = date_time

    df.to_csv(f'close_prices_1y_{SYMBOL_INPUT}.csv')

    f = open(f'close_prices_1y_{SYMBOL_INPUT}.csv', 'r')
    df = pd.read_csv(f)
    close_position(ac.trade_statement_buy, ac.trade_statement_sell)
    if 35 < df['RSI'].iat[-1] < 65:
        print(
            f'{df["PERIODS"].iat[-1]}ВРЕМЯ: {df["TIME"].iat[-1]} | ЦЕНА: {df["PRICE"].iat[-1]}'
            f'| RSI: {df["RSI"].iat[-1]}|'f' BALANCE: {check_balance("USDT")}')

    else:

        if df['RSI'].iat[-1] <= 35 and ac.trade_statement_sell is False and ac.trade_statement_buy is False \
                and ac.trade_statement_buy_stoploss is False:
            print(
                f'ВРЕМЯ: {df["TIME"].iat[-1]} | ЦЕНА: {df["PRICE"].iat[-1]}| RSI: {df["RSI"].iat[-1]}|'
                f' BALANCE: {check_balance("USDT")} - ОТКРЫТА СДЕЛКА НА ПОКУПКУ ')
            buy()
            ac.trade_statement_sell_stoploss = False
            ac.trade_statement_buy_stoploss = False
        elif df['RSI'].iat[-1] >= 65 and ac.trade_statement_buy is True and ac.trade_statement_sell is False:
            print(
                f'ВРЕМЯ: {df["TIME"].iat[-1]} | ЦЕНА: {df["PRICE"].iat[-1]}| RSI: {df["RSI"].iat[-1]}|'
                f' BALANCE: {check_balance("USDT")} - ЗАКРЫТА СДЕЛКА НА ПОКУПКУ ')
            close_buy_trade()
        elif df['RSI'].iat[-1] >= 65 and ac.trade_statement_buy is False and ac.trade_statement_sell is False \
                and ac.trade_statement_sell_stoploss is False:

            print(
                f'ВРЕМЯ: {df["TIME"].iat[-1]} | ЦЕНА: {df["PRICE"].iat[-1]}| RSI: {df["RSI"].iat[-1]}|'
                f' BALANCE: {check_balance("USDT")} - ОТКРЫТА СДЕЛКА НА ПРОДАЖУ ')
            sell()
            ac.trade_statement_sell_stoploss = False
            ac.trade_statement_buy_stoploss = False
        elif df['RSI'].iat[-1] <= 35 and ac.trade_statement_sell is True and ac.trade_statement_buy is False:
            print(
                f'ВРЕМЯ: {df["TIME"].iat[-1]} | ЦЕНА: {df["PRICE"].iat[-1]}| RSI: {df["RSI"].iat[-1]}|'
                f' BALANCE: {check_balance("USDT")} - ЗАКРЫТА СДЕЛКА НА ПРОДАЖУ ')
            close_sell_trade()

        else:
            print(
                f'ВРЕМЯ: {df["TIME"].iat[-1]} | ЦЕНА: {df["PRICE"].iat[-1]}| RSI: {df["RSI"].iat[-1]}|'
                f' BALANCE: {check_balance("USDT")}')

    time.sleep(1)
