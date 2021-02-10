import pandas as pd
from pandas_datareader import data as web
import numpy as np
import datetime
from forex_python.converter import CurrencyRates


# Date-time considerations
today = datetime.datetime.today()
yesterday = today - datetime.timedelta(days=1)

# List of average annual inflation values (defunct)
# RPI = [item for sublist in pd.read_csv('C:/Users/Tom/Desktop/ukrpi.csv').values for item in sublist]


# Function to load in assets from csv file
def load_assets():

    try:
        myassets = pd.read_csv("myassets.csv",
                                index_col=False,
                                dtype=str)
    except Exception:
        myassets = pd.DataFrame(dtype=str)

    return myassets


# Function to add an asset into the asset table requiring the ticker, number of shares and currency
def add_asset(ticker, shares, currency):
    myassets = load_assets()
    print("What asset class is this? We currently have:" + str([key for key, value in myassets.items()]))
    asset_class = input()
    myassets[asset_class][int(myassets[asset_class].last_valid_index()) +1] = f'{ticker}#{shares}/{currency}'
    df = pd.concat([pd.Series(y,name=x) for x,y in myassets.items()], axis=1)
    df.to_csv('myassets.csv',
              index=False)


# Function to fetch the exchange rate for a currency pair
def exch(cur1, cur2):

    c = CurrencyRates()
    return c.get_rate(cur1, cur2)


# Function to strip a string to any float contained within it
def striptonums(string):
    return float(''.join(c for c in string if (c.isdigit() or c == ',')))


# Desired asser weightings (gold, bonds, emerging market stocks, eu value stocks)
weights = np.array([0.2, 0.2, 0.2, 0.4])


# Function to obtain the close price of various assets stored in the asset DataFrame
def getvalue(assetdf):

    newdata = pd.DataFrame()  # Empty DataFrame for new data

    for group in assetdf.columns:

        for stock in assetdf[group].dropna():  # Iterating over the asset DataFrame ignoring NaN values

            ticker = str(stock).split('#')[0]  # Parsing the information contained in each string
            num = float(striptonums(stock))    #
            curr = stock.split('/')[1]         #

            try:
                stockdata = pd.DataFrame(web.DataReader(ticker,
                                                        data_source='yahoo',
                                                        start=yesterday,
                                                        end=today)['Adj Close'])  # Reading the data from Yahoo Finance

                stockdata.columns = [ticker + "_price"]  # Giving a name to the initial column
                stockdata[ticker + "_shares"] = num  # Adding number of shares to DataFrame

                if curr == 'GBX':
                    stockdata[ticker + "_price"] /= 100  # Converting to pounds if the currency is pennies

                elif curr != 'GBP':
                    stockdata[ticker + "_price"] /= exch('GBP', curr)  # Converting any other currency

                stockdata[ticker + "_value"] = num*stockdata[ticker + "_price"]  # Calculating the value of stocks held
                newdata = pd.concat([newdata, stockdata], axis=1)  # adding each stockdata to newdata
                print(stockdata)
                print("\n")

            except KeyError:
                print(f"Stock {ticker} not found")  # Exception if the data reader cannot find the ticker in question
                pass

    newdata.index = pd.to_datetime(newdata.index)  # Converting the index of the DataFrame to a datetime series
    try:
        olddata = pd.read_csv('valuedf.csv',
                              index_col=0,
                              parse_dates=True,
                              dayfirst=True,
                              dtype=float)  # Reading in the old data
    except Exception:
        # Exception to create a blank DataFrame if the old data csv file is empty
        olddata = pd.DataFrame()

    # Adding the new data onto the old data
    olddata = pd.concat([olddata, newdata], axis=0,)

    # Filtering out any duplicate rows
    olddata= olddata[~olddata.index.duplicated(keep="last")]

    # Writing the data back into the csv file
    olddata.to_csv('valuedf.csv')
    return olddata

getvalue(load_assets())

