import numpy as np
import pandas as pd
import pickle

ERROR_VALUE = 0.0001


## Now we enter the data analysis phase
# We could also load our_data manually from the file.
# year = input("What year would you like to look at? ")
# month = input("What month would you like to look at? (Type the number of the month, i.e 10 for October ")
year, month = 2022, 10

with open(f"Snp500_stock_dict_{month}_{year}", "rb") as f:
    our_data = pickle.load(f)

data = pd.DataFrame(our_data)
data = data.transpose()
data.index.name = "Symbol"


## DATA ANALYSIS IS BELOW

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


def change_score_formula(stock_dictionary):
    """ If we decide we want different criteria for our score then this function will
    rescore all of our stock variables """
    output_dict = stock_dictionary
    for key, value in stock_dictionary.items():
        # key = stock_name, value = the stock data,
        debt_to_equity = value["debt to equity"]
        price_to_sales = value["price to sales"]
        pe_ratio = value["pe ratio"]
        beta = value["beta"]

        score = 0
        score += calculate_score(debt_to_equity, 1, 2)
        score += calculate_score(price_to_sales, 3, 5)
        score += calculate_score(pe_ratio, 25, 35)
        score += calculate_score(beta, 1.5, 10)
        output_dict[key]["score"] = score

    return output_dict


good_stocks = {}
good_stock_count = 0
for key, value in our_data.items():
    if value["score"] == 0:
        good_stock_count += 1
        value.pop("score")
        value.pop("beta")
        good_stocks[key] = value
print(f"there are {good_stock_count} good stocks")
df = pd.DataFrame(good_stocks)
df = df.transpose()
df.index.rename = "Symbol"


def add_rank_columns(dataframe, column_name):
    count = 0
    ranks = []
    new_df = dataframe.sort_values(column_name)
    for _ in new_df.iterrows():
        count += 1
        ranks.append(count)
    new_df[f"{column_name} rank"] = ranks
    return new_df


df = add_rank_columns(df, "pe ratio")
df = add_rank_columns(df, "debt to equity")
df = add_rank_columns(df, "price to sales")
df["total_score"] = df["pe ratio rank"] + df["debt to equity rank"] + df["price to sales rank"]

df = df.sort_values("total_score")

print(df)
df.to_csv(f"Best stocks for {month}_{year}")
# The lowest score stocks are the best, this output should change every month
