# Monthly-Value-Stock-Finder
After adding in your own alphavantage api key you will be able to scan the S&P 500 for stocks that meet an adjustable value investing criteria.

In data_collection.py we webscrape from Stratosphere and use alphavantage to get our stock data from each stock taken from the S&P 500 list on wikipedia.
We then process the data in main.py. Every stock that meets our criteria is given a ranking for the criteria we want to select from. These ranks are then added up to find the best 5 value stocks. (A lower score is better)
This program is designed to be run every month and could influence your investing decisions.
