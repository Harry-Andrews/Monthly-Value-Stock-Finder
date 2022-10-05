import bs4 as bs
import requests
import time
import datetime as dt
import pickle
from secret_information import STOCK_API_KEY

ERROR_VALUE = 0.0001 #This is the value that gets added to our data if we cannot find what we are looking for.

wiki_response = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
soup = bs.BeautifulSoup(wiki_response.text, 'lxml')
table = soup.find('table', {'class': 'wikitable sortable'})

tickers = []
# Tickers is a variable that stores all of the stock tickers

# The code below finds the snp500 stock table on wikipedia and takes all of the stocks and adds them to tickers
# Stratosphere only accepts BF-B instead of BF.B so we have to change the stock's name manually.
for row in table.findAll('tr')[1:]:  # We skip the tr header
    ticker = row.findAll('td')[0].text
    ticker = ticker.strip()
    if ticker == "BF.B":
        ticker = "BF-B"
    elif ticker == "BRK.B":
        ticker = "BRK-B"
    tickers.append(ticker)


def get_number(string):
    """ When we receive a response from stratosphere, this isolates the number part of the
    information and returns it as a float """
    number = string.split(",")[0].split("}")[0].split(":")[1]
    return float(number)


def calculate_score(value, good_number, bad_number):
    """ This scores a particular stock's criteria, ideally we want it to be below the good number,
    however if the stock is a little bit over then the score is only increased a little bit"""
    output = 0
    if value == ERROR_VALUE:
        output += 1000
    elif value <= good_number:
        pass
    elif value < bad_number:
        percentage_off = (value - good_number) * 100
        output += percentage_off
    else:
        output += 1000
    return output

parameters = {
    "function": "overview",
    "symbol": "This is the stock we are looking for - this will change when we run the code",
    "apikey": STOCK_API_KEY,
}
# These parameters will be used when we send a request to alphavantage's API


our_data = {}
good_stocks = {}
counter = 0
# Alpha vantage only lets us send 5 requests per minute, the count variable helps us limit our requests

# For some reason KO broke the code - the stock doesnt meet our criteria anyways so
# We do not need to check it.
broken_stocks = ["KO"]
for broken_stock in broken_stocks:
    tickers.remove(broken_stock)
stocks_done = 0

for stock in tickers:
    parameters["symbol"] = stock
    stocks_done += 1
    if stocks_done > 500:
        break
    if counter == 5:
        time.sleep(11)
        # The sleep statements workout to 61 seconds of sleep between batches of 5
        # This means we are not spamming the api.
        counter = 0
    counter += 1
    print(f"Now working on {stock}")
    try:
        response = requests.get(url="https://www.alphavantage.co/query", params=parameters)
        data = response.json()
    except:
        data["PERatio"] = ERROR_VALUE
        data["Beta"] = ERROR_VALUE

    try:
        pe_ratio = float(data["PERatio"])
    except:
        pe_ratio = ERROR_VALUE
    try:
        beta = float(data["Beta"])
    except:
        beta = ERROR_VALUE
    try:
        response = requests.get("https://www.stratosphere.io/company-search/" + stock + "/")
        # We extract the data that we need from stratosphere
    except:
        response = f"totaldebtequity:{ERROR_VALUE}, pricetosales:{ERROR_VALUE}"
    time.sleep(10)  # Incase they get angry at us spamming their website - 5* 1 + 56 > 60
    try:
        debt_to_equity = response.text.split("totaldebttoequity")[1]
        debt_to_equity = get_number(debt_to_equity)
    except:
        debt_to_equity = ERROR_VALUE
    try:

        price_to_sales = response.text.split("pricetosales")[1]
        price_to_sales = get_number(price_to_sales)
    except:
        price_to_sales = ERROR_VALUE

    score = 0

    score += calculate_score(debt_to_equity, 1, 2)
    score += calculate_score(price_to_sales, 3, 5)
    score += calculate_score(pe_ratio, 25, 35)
    score += calculate_score(beta, 1, 10)

    if score <= 10:
        good_stocks[stock] = score

    mini_json = {}
    mini_json["pe ratio"] = pe_ratio
    mini_json["beta"] = beta
    mini_json["debt to equity"] = debt_to_equity
    mini_json["price to sales"] = price_to_sales
    mini_json["score"] = score
    print(mini_json)
    our_data[stock] = mini_json

# The variable our_data is a dictionary containing the data that we want for each stock
# We will save this data for later use

date = dt.datetime.today()
with open(f"Snp500_stock_dict_{date.month}_{date.year}", "wb") as f:
    pickle.dump(our_data, f)

print(f"The value stocks are: {good_stocks}")

# If we want to save our data to a csv:
data = our_data
df = data.stack().reset_index().rename(index=str, columns={"level_1": "Symbol"}).sort_values(['Symbol', 'Date'])
df = df.set_index('Date', inplace=True)

df.to_csv(f"SnP_500_Stocks{date.month}_{date.year}.csv")


