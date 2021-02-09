import pandas as pd
from pandas_datareader import data as web
import numpy as np
import matplotlib.pyplot as plt
import datetime
from IPython.display import display, HTML
import re
from forex_python.converter import CurrencyRates
import matplotlib.ticker as ticker


today = datetime.datetime.today()
yesterday = today - datetime.timedelta(days=1)


RPI = [item for sublist in pd.read_csv('C:/Users/Tom/Desktop/ukrpi.csv').values for item in sublist]


gold = ['SGLN.L#30/p']
emerg = ['HMCA.L#30/£', 'HMCH.L#60/p', 'HTWN.L#5/p']
bond = ['VGOV.L#30/£']
euvalue = ['ZPRX.DE#30/e']

myassets = {'gold': ['SGLN.L#30/p'], 'emerg': ['HMCA.L#30/£', 'HMCH.L#60/p', 'HTWN.L#5/p'], 'bond': ['VGOV.L#30/£'], 'euvalue': ['ZPRX.DE#30/e']}

# Managing exchange rates

symbtotick = {'£': 'GBP', 'e': 'EUR', '$': 'USD'}  # A dictionary to hold currency tickers

def exch(cur1, cur2):  # Function to fetch the exchange rate for a currency pair

    c = CurrencyRates()
    return c.get_rate(cur1, cur2)

def striptonums(string):
    return float(''.join(c for c in string if (c.isdigit() or c == ',')))

#Desired asser weightings (gold, bonds, emerging market stocks, eu value stocks)
weights = np.array([0.2, 0.2, 0.2, 0.4])

#dataframe for adj close price of assets



def getvalue(dict):

    olddata = pd.read_csv(r'C:\Users\Tom\Desktop\Python projects\Portfolio management tool\valuedf.csv', index_col=0)
    # df = pd.DataFrame()
    newdata = pd.DataFrame()

    for name, assets in dict.items():
        total = 0

        for stock in assets:

            ticker = stock.split('#')[0]
            num = float(striptonums(stock))
            curr = stock.split('/')[1]

            try:
                stockdata = pd.DataFrame(web.DataReader(ticker, data_source='yahoo', start=yesterday, end=today)['Adj Close'])
                stockdata.columns = [ticker + "_price"]
                stockdata[ticker + "_shares"] = num

                if curr == 'p':
                    stockdata[ticker + "_price"] /= 100

                elif curr == 'e':
                    stockdata[ticker + "_price"] /= exch('GBP', 'EUR')

                stockdata[ticker + "_value"] = num*stockdata[ticker + "_price"]
                newdata = pd.concat([newdata, stockdata], axis=1)
                print(stockdata)
                print("\n")

            except KeyError:
                None
                # total += stockdata["value"]
        # df[name][today] = total
    print(olddata)
    print(newdata)
    olddata.append(newdata)
    olddata.to_csv(r'C:\Users\Tom\Desktop\Python projects\Portfolio management tool\valuedf.csv')
    return olddata


getvalue(myassets)





# plt.show()

