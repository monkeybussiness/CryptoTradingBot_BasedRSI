from binance import Client
import pandas as pd
from datetime import datetime
import indicators
from binance.enums import HistoricalKlinesType

API_KEY = 'TOKEN_API'
SECRET_KEY = 'SECRET_KEY'
CAPS = ['Time', 'Open-', 'DATE', 'PERIOD', 'PRICE', 'Volume-', 'TIME', 'Quote asset volume-',
        'Number of trades-', 'Taker buy base asset volume-', 'Taker buy quote asset volume-', 'Ignore-']

client = Client(API_KEY, SECRET_KEY)
future_balance = client.futures_account_balance()
SYMBOL_INPUT = "KAVAUSDT"
period_time = '20 days ago UTC'
STOP_LOSS_PERCENT = 1


class Account:
    def __init__(self, balance, trade_statement_buy, trade_statement_sell, count_of_coin, trade_sum, open_trade_price,
                 unrealized_profit):
        self.balance = balance
        self.trade_statement_buy = trade_statement_buy
        self.trade_statement_sell = trade_statement_sell
        self.count_of_coin = count_of_coin
        self.trade_sum = trade_sum
        self.open_trade_price = open_trade_price
        self.unrealized_profit = unrealized_profit


def buy(buy_price):
    ac.trade_statement_buy = True
    ac.trade_statement_sell = False
    ac.trade_sum = ac.balance
    ac.balance = ac.balance - ac.trade_sum
    ac.count_of_coin = ac.trade_sum / buy_price
    ac.open_trade_price = buy_price

    print(
        f'ВРЕМЯ: {df["TIME"][i]} | ЦЕНА: {df["PRICE"][i]}| RSI: {df["RSI"][i]}|'
        f' BALANCE: {ac.balance} - ОТКРЫТА СДЕЛКА НА ПОКУПКУ НА СУММУ: {round(ac.trade_sum, 2)}$ ПО ЦЕНЕ : {ac.open_trade_price}')


def sell(sell_price):
    ac.trade_statement_sell = True
    ac.trade_statement_buy = False
    ac.trade_sum = ac.balance
    ac.balance = ac.balance - ac.trade_sum
    ac.count_of_coin = ac.trade_sum / sell_price
    ac.open_trade_price = sell_price
    print(
        f'ВРЕМЯ: {df["TIME"][i]} | ЦЕНА: {df["PRICE"][i]}| RSI: {df["RSI"][i]}|'
        f' BALANCE: {ac.balance} - ОТКРЫТА СДЕЛКА НА ПРОДАЖУ НА СУММУ: {round(ac.trade_sum, 2)}$')


def close_buy_trade(balance, close_buy_price, count_of_coin, trade_sum):
    ac.trade_statement_buy = False
    ac.trade_statement_sell = False
    profit = (count_of_coin * close_buy_price) - trade_sum
    ac.balance = balance + profit + ac.trade_sum
    stop_loss = ac.open_trade_price * count_of_coin * STOP_LOSS_PERCENT
    profit_precentage = stop_loss
    print(
        f'ВРЕМЯ: {df["TIME"][i]} | ЦЕНА: {df["PRICE"][i]}| RSI: {df["RSI"][i]}|'
        f' BALANCE: {ac.balance} - ЗАКРЫЛ СДЕЛКУ НА ПОКУПКУ| ПРОФИТ: {profit}')


def close_sell_trade(balance, close_sell_price, count_of_coin, trade_sum):
    ac.trade_statement_buy = False
    ac.trade_statement_sell = False
    profit = trade_sum - (count_of_coin * close_sell_price)
    ac.balance = ac.balance = balance + profit + ac.trade_sum
    print(
        f'ВРЕМЯ: {df["TIME"][i]} | ЦЕНА: {df["PRICE"][i]}| RSI: {df["RSI"][i]}|'
        f' BALANCE: {ac.balance} - ЗАКРЫЛ СДЕЛКУ НА ПРОДАЖУ| ПРОФИТ: {profit}')


now = datetime.now()
current_time = now.strftime("%H:%M:%S")
price = []
periods = []
time_list = []
date_time = []

timestamp = client._get_earliest_valid_timestamp(f'{SYMBOL_INPUT}', '1m', )
bars = client.get_historical_klines(SYMBOL_INPUT, '1m', '30 days ago',
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

ac = Account(balance=7, trade_statement_buy=False, trade_statement_sell=False, count_of_coin=0, trade_sum=0,
             open_trade_price=0, unrealized_profit=0)

for i in range(len(df["RSI"])):
    if 35 < df['RSI'][i] < 65:
        print(
            f'ВРЕМЯ: {df["TIME"][i]} | ЦЕНА: {df["PRICE"][i]}| RSI: {df["RSI"][i]}|'
            f' BALANCE: {ac.balance}')
    else:
        if df['RSI'][i] <= 35 and ac.trade_statement_sell is False and ac.trade_statement_buy is False:
            buy(buy_price=df['PRICE'][i])
        elif df['RSI'][i] >= 65 and ac.trade_statement_buy is True and ac.trade_statement_sell is False:
            close_buy_trade(ac.balance, df['PRICE'][i],
                            ac.count_of_coin, ac.trade_sum)
        elif df['RSI'][i] >= 65 and ac.trade_statement_buy is False and ac.trade_statement_sell is False:
            sell(sell_price=df['PRICE'][i])
        elif df['RSI'][i] <= 35 and ac.trade_statement_sell is True and ac.trade_statement_buy is False:
            close_sell_trade(balance=ac.balance, close_sell_price=df['PRICE'][i],
                             count_of_coin=ac.count_of_coin,
                             trade_sum=ac.trade_sum)
        else:
            continue
final_balance = ac.balance + ac.trade_sum
final_profit = final_balance - 7
final_profit_percenteges = round((final_profit / 7) * 100, 2)
print(
    f"ИТОГОВЫЙ БАЛАНС: {final_balance} | ИТОГОВЫЙ ПРОФИТ: {final_profit}| ПРОЦЕНТЫ: {final_profit_percenteges}% за "
    f"{period_time} ")
