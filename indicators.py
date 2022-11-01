import pandas as pd


def SMA(data, ndays):
    SMA = pd.Series(data['Close'].rolling(ndays).mean(), name='SMA')
    data = data.join(SMA)
    return data


# Exponentially-weighted Moving Average
def EWMA(data, ndays):
    EMA = pd.Series(data['Close'].ewm(span=ndays, min_periods=ndays - 1).mean(),
                    name='EWMA_' + str(ndays))
    data = data.join(EMA)
    return data


def rsi(df, periods=14, ema=True):
    df = df.astype(float)

    close_delta = df['PRICE'].diff()

    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)

    if ema:
        ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
        ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    else:
        ma_up = up.rolling(window=periods, adjust=False).mean()
        ma_down = down.rolling(window=periods, adjust=False).mean()

    rsi = ma_up/ma_down
    rsi = 100-(100/(1+rsi))

    return rsi


