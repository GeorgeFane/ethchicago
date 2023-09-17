# ======================================================================================================================
# IMPORTS
# ======================================================================================================================

import backtrader as bt
from datetime import datetime
from dateutil.relativedelta import relativedelta
import io
import pandas as pd
import requests
from datetime import date, timedelta
import openai
# ======================================================================================================================
# CONFIGURATION
# ======================================================================================================================

# Set your Amberdata API_KEY here
Amberdata_API_KEY = 'UAT1f4d13dd25813bd39de7e205aca3850c'

# Set initial capital
icap = 100000

# Set position size - Percent of capital to deploy per trade
PercSize = 100

# Set percent trailing stop
PercTrail = 0.40

# Timeframe for the analysis
today = date.today()
start_date = str(today.replace(year=today.year-5))
end_date = str(today)


# ======================================================================================================================
# HELPERS - DATA SOURCES
# ======================================================================================================================

class CustomPandas(bt.feeds.PandasData):
    # Add a 'stf' line to the inherited ones from the base class
    lines = ('stf',)

    # openinterest in GenericCSVData has index 7 ... add 1
    # add the parameter to the parameters inherited from the base class
    # params = (('stf2sd', 8),)
    params = (('stf', 8),)

# Call Amberdata's API


def amberdata(url, queryString, apiKey):
    try:
        headers = {'x-api-key': apiKey}
        response = requests.request(
            "GET", url, headers=headers, params=queryString)
        return response.text
    except Exception as e:
        raise e

# Get Market data from Amberdata


def amberdata_ohlcv(exchange, symbol, startDate, endDate):
    format = "%Y-%m-%dT%H:%M:%S"
    startTimestamp = datetime.strptime(startDate, '%Y-%m-%d')
    endTimestamp = datetime.strptime(endDate, '%Y-%m-%d')

    current = startTimestamp
    next = current
    fields = "timestamp,open,high,low,close,volume"
    payload = fields
    while (current < endTimestamp):
        next += relativedelta(years=1)
        if (next > endTimestamp):
            next = endTimestamp
        print('Retrieving OHLCV between', current, ' and ', next)
        result = amberdata(
            "https://web3api.io/api/v2/market/ohlcv/" + symbol + "/historical",
            {"exchange": exchange, "timeInterval": "days", "timeFormat": "iso", "format": "raw_csv",
                "fields": fields, "startDate": current.strftime(format), "endDate": next.strftime(format)},
            Amberdata_API_KEY
        )
        payload += "\n" + result
        current = next

    return payload

# Get On-chain data from Amberdata - Stock to flow valuation model


def amberdata_stf(symbol, startDate, endDate):
    print('Retrieving STF between', startDate, ' and ', endDate)
    return amberdata(
        "https://web3api.io/api/v2/market/metrics/" + symbol + "/valuations/historical",
        {"format": "csv", "timeFrame": "day",
            "startDate": startDate, "endDate": endDate},
        Amberdata_API_KEY
    )


def to_pandas(csv):
    return pd.read_csv(io.StringIO(csv), index_col='timestamp', parse_dates=True)


# ======================================================================================================================
# HELPERS - TRADING
# ======================================================================================================================

def pretty_print(format, *args):
    print(format.format(*args))


def exists(object, *properties):
    for property in properties:
        if not property in object:
            return False
        object = object.get(property)
    return True


def printTradeAnalysis(cerebro, analyzers):
    format = "  {:<24} : {:<24}"
    NA = '-'

    print('Backtesting Results')
    if hasattr(analyzers, 'ta'):
        ta = analyzers.ta.get_analysis()

        openTotal = ta.total.open if exists(ta, 'total', 'open') else None
        closedTotal = ta.total.closed if exists(
            ta, 'total', 'closed') else None
        wonTotal = ta.won.total if exists(ta, 'won',   'total') else None
        lostTotal = ta.lost.total if exists(ta, 'lost',  'total') else None

        streakWonLongest = ta.streak.won.longest if exists(
            ta, 'streak', 'won',  'longest') else None
        streakLostLongest = ta.streak.lost.longest if exists(
            ta, 'streak', 'lost', 'longest') else None

        pnlNetTotal = ta.pnl.net.total if exists(
            ta, 'pnl', 'net', 'total') else None
        pnlNetAverage = ta.pnl.net.average if exists(
            ta, 'pnl', 'net', 'average') else None

        pretty_print(format, 'Open Positions', openTotal or NA)
        pretty_print(format, 'Closed Trades',  closedTotal or NA)
        pretty_print(format, 'Winning Trades', wonTotal or NA)
        pretty_print(format, 'Loosing Trades', lostTotal or NA)
        print('\n')

        pretty_print(format, 'Longest Winning Streak',
                     streakWonLongest or NA)
        pretty_print(format, 'Longest Loosing Streak',
                     streakLostLongest or NA)
        pretty_print(format, 'Strike Rate (Win/closed)', (wonTotal /
                     closedTotal) * 100 if wonTotal and closedTotal else NA)
        print('\n')

        pretty_print(format, 'Inital Portfolio Value', '${}'.format(icap))
        pretty_print(format, 'Final Portfolio Value',
                     '${}'.format(cerebro.broker.getvalue()))
        pretty_print(format, 'Net P/L',
                     '${}'.format(round(pnlNetTotal,   2)) if pnlNetTotal else NA)
        pretty_print(format, 'P/L Average per trade',
                     '${}'.format(round(pnlNetAverage, 2)) if pnlNetAverage else NA)
        print('\n')

    if hasattr(analyzers, 'drawdown'):
        pretty_print(format, 'Drawdown', '${}'.format(
            analyzers.drawdown.get_analysis()['drawdown']))
    if hasattr(analyzers, 'sharpe'):
        pretty_print(format, 'Sharpe Ratio:',
                     analyzers.sharpe.get_analysis()['sharperatio'])
    if hasattr(analyzers, 'vwr'):
        pretty_print(format, 'VRW', analyzers.vwr.get_analysis()['vwr'])
    if hasattr(analyzers, 'sqn'):
        pretty_print(format, 'SQN', analyzers.sqn.get_analysis()['sqn'])
    print('\n')

    print('Transactions')
    format = "  {:<24} {:<24} {:<16} {:<8} {:<8} {:<16}"
    pretty_print(format, 'Date', 'Amount', 'Price', 'SID', 'Symbol', 'Value')
    for key, value in analyzers.txn.get_analysis().items():
        pretty_print(format, key.strftime("%Y/%m/%d %H:%M:%S"),
                     value[0][0], value[0][1], value[0][2], value[0][3], value[0][4])


# ======================================================================================================================
# STRATEGY
# ======================================================================================================================

# class Strategy(bt.Strategy):
#     params = (
#         ("short_period", 50),
#         ("long_period", 200),
#     )

#     def __init__(self):
#         self.short_ma = bt.indicators.SimpleMovingAverage(
#             self.data.close, period=self.params.short_period
#         )
#         self.long_ma = bt.indicators.SimpleMovingAverage(
#             self.data.close, period=self.params.long_period
#         )

#     def next(self):
#         if self.short_ma > self.long_ma and not self.position:
#             # Generate a buy signal and execute the order
#             self.buy()
#         elif self.short_ma < self.long_ma and self.position:
#             # Generate a sell signal and execute the order
#             self.sell()


# ======================================================================================================================
# MAIN
# ======================================================================================================================    

def main(data_text):
    # Create an instance of cerebro
    cerebro = bt.Cerebro(stdstats=False)

    # Import OpenAI
    openai.api_key = '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'
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a technical analyst that will provide a python class that implements a\
            trading algorithm based on text input from a user using the backtrader python module. The class will follow\
            the following format and inheret from backtest: Strategy: class Strategy(bt.Strategy): params = () def __init__(self): def next(self):"},
            {"role": "user", "content": "{}".format(data_text)}, 
        ]
    )
    # Provide me a strategy that takes advantage of moving averages
    python_code = response['choices'][0]['message']['content'].split(r"```")[1]
    class_renamed = "class Strategy(" + "(".join(python_code.split("(")[1:])
#     class_renamed = """
# # class Strategy(bt.Strategy):
# #     params = (
# #         ("short_period", 50),
# #         ("long_period", 200),
# #     )

# #     def __init__(self):
# #         self.short_ma = bt.indicators.SimpleMovingAverage(
# #             self.data.close, period=self.params.short_period
# #         )
# #         self.long_ma = bt.indicators.SimpleMovingAverage(
# #             self.data.close, period=self.params.long_period
# #         )

# #     def next(self):
# #         if self.short_ma > self.long_ma and not self.position:
# #             # Generate a buy signal and execute the order
# #             self.buy()
# #         elif self.short_ma < self.long_ma and self.position:
# #             # Generate a sell signal and execute the order
# #             self.sell()

# # """
    print(class_renamed)

    exec(class_renamed, globals(), globals())

    # Be selective about what we chart
    # cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.Value)
    cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.Trades)

    # Set the investment capital
    cerebro.broker.setcash(icap)

    # Set position size
    cerebro.addsizer(bt.sizers.PercentSizer, percents=PercSize)

    # Add our strategy
    cerebro.addstrategy(Strategy)

    # Read market and on-chain data into dataframe
    btc = to_pandas(amberdata_ohlcv("gdax", "btc_usd", start_date, end_date))
    btc_stf = to_pandas(amberdata_stf("btc", start_date, end_date))
    btc['stf'] = btc_stf['price']

    # Feed Cerebro our data
    # cerebro.adddata(CustomPandas(dataname=btc, openinterest=None, stf2sd='stf2sd'))
    cerebro.adddata(CustomPandas(dataname=btc, openinterest=None, stf='stf'))

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe',
                        riskfreerate=0.0, annualize=True, timeframe=bt.TimeFrame.Days)
    cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
    cerebro.addanalyzer(bt.analyzers.Transactions, _name='txn')

    # Run our Backtest
    backtest = cerebro.run()
    backtest_results = backtest[0]

    # Print some analytics
    printTradeAnalysis(cerebro, backtest_results.analyzers)

    txns = [
        (
            key.strftime("%Y/%m/%d"),
            round(value[0][0], 2),
            value[0][1],
            round(value[0][4], 2),
        )
        for key, value
        in backtest_results.analyzers.txn.get_analysis().items()
    ]

    return {
        'initial': icap,
        'final': round(cerebro.broker.getvalue(), 2),
        'txns': txns,
        'sharpe': backtest_results.analyzers.sharpe.get_analysis()['sharperatio'],
        'sqn': backtest_results.analyzers.sqn.get_analysis()['sqn'],
        'vwr': backtest_results.analyzers.vwr.get_analysis()['vwr'],
        'code': class_renamed,
    }

    # Finally plot the end results
    # cerebro.plot(style='candlestick', volume=False)

# ======================================================================================================================