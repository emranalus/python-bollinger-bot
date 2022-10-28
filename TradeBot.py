from binance.client import Client
import pandas as pd
import config
import time

client = Client(api_key='API PUBLIC KEY HERE', api_secret='API SECRET KEY HERE')

# Parametreler
print("WARNING: Only USDT parities are allowed!")
sembol = input("Enter Parity(ex. ETHUSDT): ")
sellSembol = sembol[:-4]
isInPosition = False

def nekadarCoinAlinir(bakiye, fiyat):
    buy_quant = bakiye / float(fiyat)
    return buy_quant


def get_quantity_precision(currency_symbol):    
    info = client.get_exchange_info() 
    info = info['symbols']
    for x in range(len(info)):
        if info[x]['symbol'] == currency_symbol:
            return info[x]['pricePrecision']
    return None


def bakiyem():
    return float(client.get_asset_balance('USDT')['free'])


def guncelfiyat(symbol):
    return client.get_symbol_ticker(symbol=symbol)['price']


def buyOrder():
    try:
        client.create_order(symbol=sembol,
                            side=Client.SIDE_BUY,
                            type=Client.ORDER_TYPE_MARKET,
                            quantity=round(float(round(nekadarCoinAlinir(bakiyem(), guncelfiyat(sembol)), 5)) * 0.98,
                                           get_quantity_precision(sembol)))
        print("BUY ORDER: " + str(guncelfiyat(sembol)) + " " + sembol)
    except:
        time.sleep(5)
        client.create_order(symbol=sembol,
                            side=Client.SIDE_BUY,
                            type=Client.ORDER_TYPE_MARKET,
                            quantity=round(float(round(nekadarCoinAlinir(bakiyem(), guncelfiyat(sembol)), 5)) * 0.98,
                                           get_quantity_precision(sembol)))
        print("BUY ORDER: " + str(guncelfiyat(sembol)) + " " + sembol)


def sellOrder():
    try:
        client.create_order(symbol=sembol,
                            side=Client.SIDE_SELL,
                            type=Client.ORDER_TYPE_MARKET,
                            quantity=round(float(client.get_asset_balance(sellSembol)['free']) * 0.99, get_quantity_precision(sembol)))
        print("SELL ORDER: " + str(guncelfiyat(sembol)) + " " + sembol)
    except:
        time.sleep(5)
        client.create_order(symbol=sembol,
                            side=Client.SIDE_SELL,
                            type=Client.ORDER_TYPE_MARKET,
                            quantity=round(float(client.get_asset_balance(sellSembol)['free']) * 0.99, get_quantity_precision(sembol)))
        print("SELL ORDER: " + str(guncelfiyat(sembol)) + " " + sembol)


def getMinuteData(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback + ' min ago UTC'))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


def applyTechnicals(df):
    # Hesaplama
    df['SMA'] = df.Close.rolling(20).mean()
    df['stddev'] = df.Close.rolling(20).std()

    df['Upper'] = df.SMA + 2 * df.stddev
    df['Lower'] = df.SMA - 2 * df.stddev

    df.dropna(inplace=True)


print("Trade Bot Çalışmaya Başlıyor...")
# Main Programme
while True:
    # Parite, Timeframe, Lookback(En son mum artı ne kadar geriye baksın{Mesela en son mum ve 100 önceki mum})
    df = getMinuteData(sembol, '5m', '20000')
    applyTechnicals(df)

    # Main Program
    # LONG ENTER
    if isInPosition == False and df["Lower"][-1] > df["open"][-1]:
        buyOrder()
        isInPosition = True

    # LONG EXIT
    if isInPosition and df["Upper"][-1] < df["open"][-1]:
        sellOrder()
        isInPosition = False

    time.sleep(3)
