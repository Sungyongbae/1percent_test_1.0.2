import time
import pyupbit
import datetime
import pandas as pd
import telegram

TOKEN = '1919980133:AAG845Pwz1i4WCJvaaamRT-_QE0uezlvA9A'
ID = '-548871861'
bot = telegram.Bot(TOKEN)


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def get_price(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    df['volatility'] = (df['close']/df['open']-1)*100
    volatility = df.iloc[-1]['volatility']
    return volatility

def get_top5(rq):
    tickers = pyupbit.get_tickers(fiat="KRW")
    dfs = []
    for i in range(len(tickers)):
        volatility = round(get_price(tickers[i]),2)
        dfs.append(volatility)
        time.sleep(0.06)

    volatility = pd.DataFrame({"volatility": dfs})
    ticker = pd.DataFrame({"ticker": pyupbit.get_tickers(fiat="KRW")})
    sum = [ticker, volatility]
    all_volatility = pd.concat(sum, axis =1)
    final=all_volatility.sort_values(by = "volatility", ascending=False)
    if rq == 0:
        #Dataframe을 list로 변환
        #result = final.iloc[:5]
        result = final.iloc[0].values.tolist()
    elif rq ==1:
        #상위 상승률 top5 ticker명만 뽑기
        result1 = final.iloc[:5]['ticker'].values.tolist()
    else:
        #상위 상승률 top5 상승률만 뽑기
        result2 = final.iloc[:5]['volatility'].values.tolist()
    return result[0]

def check_profit(ticker,price,total):
    buy_value = price * total
    current_price = get_current_price(ticker)
    current_value = current_price * total
    profit = round(((current_value/buy_value)-1)*100,2)
    return profit

# 시작 메세지 텔레그램 전송
bot.sendMessage(ID, "1percent_autotrade start")

check_buy = False
check_success = False
check_fail = False
my_money = 1000000

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-ETH")
        end_time = start_time + datetime.timedelta(days=1)
        if start_time < now < end_time - datetime.timedelta(seconds=5):
            if check_buy == False and check_success == False and my_money> 5000:
                ticker = get_top5(0)
                current_price = get_current_price(ticker)
                buy_date = now.strftime('%b/%d')
                buy_ticker = ticker
                buy_price =  current_price 
                buy_total =(my_money*0.9995*0.996)/buy_price
                bot.sendMessage(ID, str(buy_ticker) + '\n'
                                    + "buy price:" + str(buy_price) + '\n'
                                    + "buy total:" + str(buy_total) + '\n'
                                    + "test...ing")
                my_money = 0
                check_buy = True 
            elif check_buy == True:
                current_profit = check_profit(buy_ticker,buy_price,buy_total)
                if current_profit >= 1.8:
                    sell_price = get_current_price(buy_ticker)
                    my_money = sell_price*(buy_total*0.9995*0.996)
                    bot.sendMessage(ID, str(buy_ticker) + '\n'
                                    + "sell price:" + str(sell_price) + '\n'
                                    + "my_money:" + str(my_money) + '\n'
                                    + "1percent success" + '\n'
                                    + "test...ing")
                    check_success = True
                    check_buy = False
                    check_fail = False
                elif current_profit <= (-2.0):
                    fail_price = get_current_price(buy_ticker)
                    fail_profit = check_profit(buy_ticker,buy_price,buy_total)
                    my_money = fail_price*(buy_total*0.9995*0.996)
                    bot.sendMessage(ID, str(buy_ticker) + '\n'
                                        + "current price:" + str(fail_price) + '\n'
                                        + "profit:" + str(fail_profit) + '\n'
                                        + "rest_money:" + str(my_money) + '\n'
                                        + str(buy_date) + "_fail" + '\n'
                                        + "test...ing")
                    check_success = True
                    check_buy = False
                    check_fail = True
        else:
            if check_success == True:
                if check_fail == False:
                    bot.sendMessage(ID, str(buy_date) + '_Congratulation'+ '\n'
                                        + "test...ing")
                    my_money = sell_price*(buy_total*0.9995*0.996)
                    check_success = False
                    check_buy = False
                else:
                    bot.sendMessage(ID, str(buy_date) + '_Need Improvement'+ '\n'
                                        + "test...ing")
                    check_success = False
                    check_buy = False
                    check_fail = False
            else:
                fail_price = get_current_price(buy_ticker)
                my_money = fail_price*(buy_total*0.9995*0.996) 
                bot.sendMessage(ID, str(buy_date) + '_initialization...'+ '\n'
                                    + "rest_money:" + str(my_money) + '\n'
                                    + "test...ing")
                check_success = False
                check_buy = False
                check_fail = False
        time.sleep(1)
    except Exception as e:
        print(e)
        bot.sendMessage(ID, e)
        time.sleep(1)
